from engrate_sdk.utils import log
from fastapi import APIRouter

from src.model import PowerTariffSpec
from src.utils import PowerTariffSvc, CountryCode

logger = log.get_logger(__name__)
router = APIRouter(
    tags=["Power Tariffs API"], include_in_schema=True, prefix="/power-tariffs"
)


@router.get(
    "/{country_code}/mga/{mga_code}",
    response_model=list[PowerTariffSpec],
    summary="Returns a grid area by postal code",
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
    "/{country_code}/lat/{lat}/lon/{lon}",
    response_model=list[PowerTariffSpec],
    summary="Returns a power tariffs by latitude and longitude",
    response_model_exclude_none=True,
)
async def power_tariff_by_coordinate(
    power_tariffs_service: PowerTariffSvc,
    country_code: CountryCode,
    lat: float,
    lon: float,
):
    """Fetches power tariffs by latitude and longitude"""
    return await power_tariffs_service.get_power_tariffs_by_coordinates(
        country_code, lat, lon
    )


@router.get(
    "/{country_code}/address/{address}/city/{city}",
    response_model=list[PowerTariffSpec],
    summary="Returns a power tariffs by address",
    response_model_exclude_none=True,
)
async def power_tariff_by_address(
    power_tariffs_service: PowerTariffSvc,
    country_code: CountryCode,
    address: str,
    city: str,
):
    """Fetches power tariffs by address"""
    return await power_tariffs_service.get_power_tariffs_by_address(
        country_code, address, city
    )
