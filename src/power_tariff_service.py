from src.model import GridOperatorSpec, PowerTariffSpec
from src.clients import elomraden
from src.repositories.power_tariffs_repository import PowerTariffRepository


class PowerTariffService:
    """
    Service class for managing power tariffs.
    """

    def __init__(self, repository: PowerTariffRepository):
        self.repository = repository

    async def get_power_tariffs_by_mga(
        self, country_code: str, mga_code: str
    ) -> list[PowerTariffSpec]:
        """
        Get a specific power tariff by its metering grid area (MGA) code.
        """
        return await self.repository.get_power_tariff_by_mga(
            country_code=country_code, mga_code=mga_code
        )

    async def get_grid_operators(self) -> list[GridOperatorSpec]:
        """
        Get all grid operators.
        """
        return await self.repository.list_operators()

    async def get_tariffs(self) -> list[PowerTariffSpec]:
        """
        Get all power tariffs definitions.
        """
        return await self.repository.list_power_tariffs()

    async def get_tariff_by_provider_id(self, provider_id) -> PowerTariffSpec:
        """
        Get a specific power tariff by provider
        """
        return await self.repository.fetch_power_tariff_by_provider_id(
            provider_id=provider_id
        )

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

    async def get_power_tariffs_by_address(
        self, country_code: str, address, town
    ) -> list[PowerTariffSpec]:
        """
        Get a specific power tariff by its postal address.
        """
        area = await elomraden.get_area_by_address(address, town)
        return await self.get_power_tariffs_by_mga(
            country_code=country_code, mga_code=area.area_code
        )

    async def get_power_tariffs_by_coordinates(
        self, country_code: str, lat: float, long: float
    ) -> list[PowerTariffSpec]:
        """
        Get a specific power tariff by its postal code.
        """
        area = await elomraden.get_area_by_coordinates(lat=str(lat), lon=str(long))
        return await self.get_power_tariffs_by_mga(
            country_code=country_code, mga_code=area.area_code
        )

    async def get_tariff_by_postal_code(self, country_code,postal_code) -> list[PowerTariffSpec]:
        """
        Get a specific power tariff by its postal code.
        """
        area = await elomraden.get_area_by_postnumber(postal_code)
        return await self.get_power_tariffs_by_mga(country_code, area.area_code)
