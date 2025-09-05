from engrate_sdk.utils import log
from fastapi import APIRouter

import env
from model import PowerTariffSpec
from src.clients import elomraden_model
from utils import PowerTariffSvc, CountryCode

logger = log.get_logger(__name__)
router = APIRouter(
    tags=["Power Tariffs API"],
    include_in_schema=True,
)


@router.get(
    "/{country_code}/mga/{mga_code}",
    response_model=list[PowerTariffSpec],
    summary="Returns a grid area by postal code",
    include_in_schema=env.is_dev_mode(),
    response_model_exclude_none=True,
)
async def power_tariff_by_mga(
    power_tariffs_service: PowerTariffSvc, country_code: CountryCode, mga_code: str
):
    """Fetches power tariffs by mga code"""
    return await power_tariffs_service.get_power_tariffs_by_mga(country_code, mga_code)


@router.get(
    "/{country_code}/postal-code/{postal_code}",
    response_model=list[PowerTariffSpec],
    summary="Returns a grid area by postal code",
    include_in_schema=env.is_dev_mode(),
    response_model_exclude_none=True,
)
async def power_tariff_by_postal_code(
    power_tariffs_service: PowerTariffSvc, countr_code: CountryCode, postal_code: int
):
    """Fetches power tariffs by mga code"""
    return await power_tariffs_service.get_tariff_by_postal_code(
        countr_code, postal_code
    )


@router.get(
    "/{country_code}/lat/{lat}/long/{long}",
    response_model=list[PowerTariffSpec],
    summary="Returns a power tariffs by latitude and longitude",
    include_in_schema=env.is_dev_mode(),
    response_model_exclude_none=True,
)
async def power_tariff_by_coordinate(
    power_tariffs_service: PowerTariffSvc,
    country_code: CountryCode,
    lat: float,
    long: float,
):
    """Fetches power tariffs by latitude and longitude"""
    return await power_tariffs_service.get_power_tariffs_by_coordinates(
        country_code, lat, long
    )


@router.get(
    "/{country_code}/address/{address}/town/{town}",
    response_model=list[PowerTariffSpec],
    summary="Returns a power tariffs by address",
    include_in_schema=env.is_dev_mode(),
    response_model_exclude_none=True,
)
async def power_tariff_by_address(
    power_tariffs_service: PowerTariffSvc,
    country_code: CountryCode,
    address: str,
    town: str,
):
    """Fetches power tariffs by address"""
    return await power_tariffs_service.get_power_tariffs_by_address(
        country_code, address, town
    )
