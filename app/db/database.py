import contextlib
from typing import Any, AsyncGenerator

from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core import logger


class DBSessionManager:
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.sessionmaker: async_sessionmaker[AsyncSession] | None = None

    def start(self, database_url: str, **pool_kwargs: Any) -> None:
        if self.engine is None:
            self.engine = create_async_engine(database_url, **pool_kwargs)
            self.sessionmaker = async_sessionmaker(
                autocommit=False, bind=self.engine, expire_on_commit=False
            )

    async def stop(self) -> None:
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.sessionmaker = None

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self.sessionmaker is None:
            raise Exception("DB session not initialized.")

        session = self.sessionmaker()
        try:
            yield session
        except Exception:
            logger.error("DB session failed, rolling back", exc_info=True)
            await session.rollback()
            raise

        finally:
            await session.close()  # Always close to return to the pool


class Base(DeclarativeBase):
    __mapper_args__ = {"eager_defaults": True}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return f"<{self.id}>"


db_session_manager = DBSessionManager()
