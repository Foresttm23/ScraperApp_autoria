from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Car(Base):
    __tablename__ = "cars"
    url: Mapped[str] = mapped_column(String, unique=True)
    title: Mapped[str] = mapped_column(String)
    price_usd: Mapped[int] = mapped_column(Integer)
    odometer: Mapped[int | None] = mapped_column(Integer)
    username: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str | None] = mapped_column(String)
    image_url: Mapped[str] = mapped_column(String)
    images_count: Mapped[int] = mapped_column(Integer)
    car_number: Mapped[str | None] = mapped_column(String(20))
    car_vin: Mapped[str | None] = mapped_column(String(17))

    datetime_found: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
