from pydantic import BaseModel, field_validator


class CarSchema(BaseModel):
    model_config = {"from_attributes": True}
    url: str
    title: str
    price_usd: int
    odometer: int | None
    username: str
    phone_number: str | None
    image_url: str
    images_count: int
    car_number: str | None
    car_vin: str | None

    @field_validator('phone_number')
    @classmethod
    def add_country_code(cls, v: str) -> str | None:
        if v is None:
            return None
        if not v.startswith("+38"):
            return "+38" + v
        return v
