import os
from dataclasses import dataclass


@dataclass
class Settings:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "db")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    FILE_DIR: str = os.getenv("FILE_DIR", "./dumps")
    FILE_NAME: str = os.getenv("FILE_NAME", "scraped_data")
    BASE_URL: str = os.getenv("BASE_URL", "https://auto.ria.com/uk/search/")
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", 3))
    SCHEDULER_HOUR: int = int(os.getenv("SCHEDULER_HOUR", 3))


    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"


settings = Settings()
