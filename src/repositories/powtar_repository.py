from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db import with_session
from src.exceptions import UnexpectedValue
from src.model import GridProviderSpec, PowerTariffSpec
from src.repositories.orm_model import (
    GridProvider,
    PowerTariff,
    PowerTariffFee,
)


class PowerTariffRepository:

    def __init__(self):
        pass
    
    @with_session
    async def list_providers(self,session:AsyncSession) -> list[GridProviderSpec]:
        """Lists all providers."""
        result = await session.execute(select(GridProvider))
        providers = result.scalars().all()
        return [provider.as_spec() for provider in providers]

    @with_session
    async def list_power_tariffs(self, session: AsyncSession) -> list[PowerTariffSpec]:
        """Fetches all power tariffs for a given provider."""
        result = await session.execute(
            select(PowerTariff)
            .options(selectinload(PowerTariff.provider))  # Load provider relationship
            .options(
                selectinload(PowerTariff.fees).
                selectinload(PowerTariffFee.compositions))
        )
        power_tariffs = result.scalars().all()
        return [power_tariff.as_spec() for power_tariff in power_tariffs]

    @with_session
    async def fetch_power_tariff_by_provider_id(self, provider_uid:UUID, session:AsyncSession) -> PowerTariffSpec:
        """Fetches all power tariffs for a given provider."""
        result = await session.execute(
            select(PowerTariff).where(PowerTariff.provider_uid == provider_uid)
        )
        power_tariffs = result.scalars().one()
        return power_tariffs.as_spec()

    @with_session
    async def fetch_power_tariff_by_provider_name(self, provider_name:str, session:AsyncSession) -> PowerTariffSpec:
        """Fetches all power tariffs for a given provider."""
        # TODO find a better way to link providers comming from elomraden
        result = await session.execute(
            select(GridProvider)
            .where(GridProvider.name.startswith(provider_name.split()[0]))
            .options(
                selectinload(GridProvider.power_tariff).
                selectinload(PowerTariff.fees).
                selectinload(PowerTariffFee.compositions)
            )
        )
        provider  = result.scalars().one_or_none()
        if provider is None:
            raise UnexpectedValue(f"Provider with name {provider_name} without power tariff definition.")
        return provider.power_tariff.as_spec()

    @with_session
    async def fetch_power_tariff_by_ediel(self, ediel:int, session:AsyncSession) -> PowerTariffSpec:
        """Fetches all power tariffs for a given provider."""
        result = await session.execute(
            select(GridProvider)
            .where(GridProvider.ediel == ediel)
            .options(
                selectinload(GridProvider.power_tariff).
                selectinload(PowerTariff.fees).
                selectinload(PowerTariffFee.compositions)
            )
        )
        provider  = result.scalars().one_or_none()
        if provider is None:
            raise UnexpectedValue(f"Provider with ediel {ediel} without power tariff definition.")
        return provider.power_tariff.as_spec()



