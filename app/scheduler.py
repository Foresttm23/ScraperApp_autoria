import asyncio
from datetime import timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.logger import logger
from app.core.settings import settings
from app.dump_data import daily_dump
from app.main import lifespan


async def scheduled_task():
    logger.info("Starting scheduled dump")
    async with lifespan():
        await daily_dump()
    logger.info("Scheduled dump completed")


async def start_scheduler():
    hour = settings.SCHEDULER_HOUR
    # hour -= 2 # We can pass time in KYIV time and then convert it to UTC

    logger.info("Scheduler started")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduled_task, 'cron', hour=hour, minute=00, timezone=timezone.utc)
    scheduler.start()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(start_scheduler())
