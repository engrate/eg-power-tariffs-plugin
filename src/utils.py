from typing import Annotated

from fastapi import Depends

from power_tariff_service import PowerTariffService
from repositories.power_tariffs_repository import PowerTariffRepository

PowerTariffSvc: type[PowerTariffService] = Annotated[PowerTariffService,
    Depends(lambda: PowerTariffService(repository=PowerTariffRepository()))]
