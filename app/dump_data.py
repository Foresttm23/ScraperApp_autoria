import asyncio
from datetime import datetime, timezone
from pathlib import Path

import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.db.car_model import Car
from app.db.database import db_session_manager

headers = list(Car.__table__.columns.keys())


async def daily_dump() -> None:
    date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    file_path = Path(settings.FILE_DIR) / f"{settings.FILE_NAME}_{date_str}.csv"

    file_path.parent.mkdir(parents=True, exist_ok=True)
    async with db_session_manager.session() as session:
        await dump_data_to_file(session, file_path)


async def dump_data_to_file(session: AsyncSession, file_path: Path) -> None:
    query = select(Car.__table__)
    data = await session.stream(query)

    async with aiofiles.open(file_path, mode='w') as f:
        await f.write(",".join(headers) + "\n")
        async for row in data:
            values = [str(val) if val is not None else "" for val in row]
            line = ",".join(values) + "\n"
            await f.write(line)


if __name__ == "__main__":
    asyncio.run(daily_dump())
