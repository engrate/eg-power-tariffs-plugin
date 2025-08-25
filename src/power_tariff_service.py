from model import GridProviderSpec
from src.clients import elomraden
from src.model import PowerTariffSpec
from src.repositories.powtar_repository import PowerTariffRepository


class PowerTariffService:
    """
    Service class for managing power tariffs.
    """

    def __init__(self, repository:PowerTariffRepository):
        self.repository = repository

    async def get_grid_providers(self) -> list[GridProviderSpec]:
        """
        Get all grid providers.
        """
        return await self.repository.list_providers()
    
    async def get_tariffs(self) -> list[PowerTariffSpec]:
        """
        Get all power tariffs definitions.
        """
        return await self.repository.list_power_tariffs()

    async def get_tariff_by_provider_id(self, provider_id) -> PowerTariffSpec:
        """
        Get a specific power tariff by provider
        """
        return await self.repository.fetch_power_tariff_by_provider_id(provider_id=provider_id)

    async def get_tariff_by_ediel(self, ediel) -> PowerTariffSpec:
        """
        Get a specific power tariff by provider
        """
        return await self.repository.fetch_power_tariff_by_ediel(ediel=ediel)

    async def get_tariff_by_provider_name(self, name) -> PowerTariffSpec:
        """
        Get a specific power tariff by provider
        """
        return await self.repository.fetch_power_tariff_by_provider_name(name)

    async def get_tariff_by_address(self, address,ort) -> PowerTariffSpec:
        """
        Get a specific power tariff by its postal address.
        """
        area = await elomraden.get_area_by_address(address,ort)
        tariff = await self.get_tariff_by_ediel(area.company.ediel)
        return tariff

    async def get_tariff_by_postal_code(self, postal_code) -> PowerTariffSpec:
        """
        Get a specific power tariff by its postal code.
        """
        area = await elomraden.get_area_by_postnumber(postal_code)
        tariff = await self.get_tariff_by_ediel(area.company.ediel)
        return tariff

