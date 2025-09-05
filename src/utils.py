from typing import Annotated

from fastapi import Depends

from src.exceptions import MissingError
from src.power_tariff_service import PowerTariffService
from src.repositories.power_tariffs_repository import PowerTariffRepository
from engrate_sdk.utils import log

logger = log.get_logger(__name__)


def validate_country_code(country_code: str) -> str:
    if country_code is None or len(country_code) != 2:
        logger.error("Country code not provided or invalid")
        raise MissingError("Country code not provided or invalid")
    return CountryCode(country_code.upper())


PowerTariffSvc: type[PowerTariffService] = Annotated[
    PowerTariffService,
    Depends(lambda: PowerTariffService(repository=PowerTariffRepository())),
]

CountryCode: type[str] = Annotated[str, Depends(validate_country_code)]
