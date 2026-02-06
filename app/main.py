import asyncio
import sys
from contextlib import asynccontextmanager

from app.core.logger import logger
from app.core.settings import settings
from app.db.database import db_session_manager, Base
from app.dump_data import daily_dump
from app.scraper import start_scraper


async def create_tables():
    async with db_session_manager.engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)

        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")


@asynccontextmanager
async def lifespan():
    # Startup
    logger.info("Startup")
    db_session_manager.start(str(settings.DATABASE_URL), pool_size=20, max_overflow=10)
    await create_tables()

    yield
    # Shutdown
    logger.info("Shutdown")
    await db_session_manager.stop()


async def main():
    async with lifespan():
        command = sys.argv[1]  # Only the first argument is used
        if command == "dump":
            await daily_dump()
            logger.info("Daily dump completed successfully!")
        elif command == "scrape":
            await start_scraper()
            logger.info("Scraping completed successfully!")
        else:
            logger.error(f"Invalid command: {command}. Allowed commands: dump, scrape")


if __name__ == '__main__':
    asyncio.run(main())
