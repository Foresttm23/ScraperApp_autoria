import re

from app.db.schemas import CarSchema


async def get_car_data(page, url) -> CarSchema:
    title = await _get_car_title(page)
    price_usd = await _get_car_price_usd(page)
    odometer = await _get_car_odometer(page)
    username = await _get_seller_username(page)
    phone = await _get_seller_phone(page)
    image_url = await _get_car_image_url(page)
    images_count = await _get_car_images_count(page)
    car_number = await _get_car_number(page)
    car_vin = await _get_car_vin(page)

    return CarSchema(url=url, title=title, price_usd=price_usd, odometer=odometer, username=username,
                     phone_number=phone, image_url=image_url, images_count=images_count, car_number=car_number,
                     car_vin=car_vin)


async def _get_car_title(page) -> str:
    title_field = page.locator("#basicInfoTitle h1").first
    title = await title_field.inner_text()
    return title


async def _get_car_price_usd(page) -> int:
    price_field = page.locator("#sidePrice strong").first
    price_raw = await price_field.inner_text()
    price_usd = int(re.sub(r"\D", "", price_raw))
    return price_usd or 0


async def _get_car_odometer(page) -> int | None:
    odometer_field = page.locator("#basicInfoTableMainInfo0 span").first
    odometer = None
    if await odometer_field.count() > 0:
        odometer_raw = await odometer_field.inner_text()
        odometer_num = int(re.sub(r"\D", "", odometer_raw))
        odometer = odometer_num * 1000 if "тис" in odometer_raw else odometer_num
    return odometer


async def _get_seller_username(page) -> str:
    username_field = page.locator("#sellerInfoUserName span").first
    username = await username_field.inner_text()
    return username or ""


async def _get_seller_phone(page) -> str | None:
    phone_popup_button = page.locator("#sellerInfo div button.conversion").first
    if await phone_popup_button.count() == 0:
        return None

    await phone_popup_button.click()

    phone_field = page.locator("#autoPhonePopUpResponse div.popup-inner button.conversion span.action").first
    await phone_field.first.wait_for()

    phone_raw = await phone_field.inner_text()
    phone = re.sub(r"\D", "", phone_raw)
    return phone or ""


async def _get_car_image_url(page) -> str:
    image_field = page.locator("#photoSlider span.picture picture img").first
    image_url = await image_field.get_attribute("data-src")
    return image_url or ""


async def _get_car_images_count(page) -> int:
    images_count_field = page.locator("#photoSlider span.alpha.medium span").nth(1)
    images_count_raw = await images_count_field.inner_text()
    images_count = int(re.sub(r"\D", "", images_count_raw))
    return images_count or 0


async def _get_car_number(page) -> str | None:
    car_number_field = page.locator("#badges div.car-number span").first
    if await car_number_field.count() == 0:
        return None

    car_number_raw = await car_number_field.inner_text()
    car_number = re.sub(r"[^a-zA-Z0-9]", "", car_number_raw)
    return car_number or ""


async def _get_car_vin(page) -> str | None:
    car_vin_field = page.locator("#badgesVinGrid div.badge-template span span.badge").first
    if await car_vin_field.count() == 0:
        return None

    car_vin_raw = await car_vin_field.inner_text()
    car_vin = re.sub(r"[^a-zA-Z0-9]", "", car_vin_raw)
    return car_vin or ""
