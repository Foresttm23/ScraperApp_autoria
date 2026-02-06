import asyncio
import logging

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log, retry_if_exception_type

from app.core.logger import logger
from app.core.settings import settings
from app.core.utils import get_car_data
from app.db.car_model import Car
from app.db.database import db_session_manager
from app.db.schemas import CarSchema


async def start_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True,
                                          args=["--disable-blink-features=AutomationControlled",
                                                "--no-sandbox", "--disable-infobars"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36")

        sem = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)

        page_num = 0
        while True:
            search_url = f"{settings.BASE_URL}?search_type=2&page={page_num}&limit=100"  # search_type=2 specifies used cars
            logger.info(f"Processing Search Page {page_num}...")
            car_links = await get_car_links(context, search_url)
            if not car_links:
                logger.info("No more cars to scrape.")
                break

            async def worker(link):
                async with sem:  # Ensures only the allowed number of requests is running at a time
                    try:
                        async with db_session_manager.session() as session:
                            await process_single_car(context, session, link)
                    except Exception as e:
                        logger.error(f"Failed to scrape car {link}: {e}")

            tasks = [worker(link) for link in car_links]
            await asyncio.gather(*tasks)
            page_num += 1
    await browser.close()


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3),
       retry=retry_if_exception_type(PlaywrightTimeout),
       before_sleep=before_sleep_log(logger, logging.WARNING))
async def get_car_links(context, url: str) -> list[str]:
    page = await context.new_page()
    try:
        await page.goto(url, timeout=30000)

        link_locator = page.locator("div#items div.items-list a.product-card")
        car_links = await link_locator.evaluate_all("els => els.map(e => e.href)")

        logger.info(f"Found {len(car_links)} cars on page.")
        return list(set(car_links))
    finally:
        await page.close()


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3),
       retry=retry_if_exception_type(PlaywrightTimeout),
       before_sleep=before_sleep_log(logger, logging.WARNING))
async def process_single_car(context, session: AsyncSession, url: str):
    page = await context.new_page()
    try:
        logger.info(f"Scraping: {url}")
        await page.goto(url, timeout=30000)

        car_data = await get_car_data(page, url)

        await save_car_record(session, car_data)
        logger.info(f"Saved: {car_data.title} from {url}")

    finally:
        await page.close()


async def save_car_record(session: AsyncSession, data: CarSchema) -> None:
    car = Car(**data.model_dump())
    session.add(car)

    try:  # Handling here specifically, so the database scripts aren't flooded with custom behavior
        await session.commit()
    except IntegrityError:
        logger.error("Skipping the duplicate", exc_info=True)
        await session.rollback()
