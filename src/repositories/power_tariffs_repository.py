from uuid import UUID

from engrate_sdk.utils import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from model import MeteringGridAreaSpec
from repositories.orm_model import (
    MeteringGridArea,
    MeteringAreaByPowerTariffs,
)
from src.db import with_session
from src.exceptions import UnexpectedValue
from src.model import GridOperatorSpec, PowerTariffSpec
from src.repositories.orm_model import (
    GridOperator,
    PowerTariff
)


class PowerTariffRepository:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @with_session
    async def list_operators(self, session:AsyncSession) -> list[GridOperatorSpec]:
        """Lists all providers."""
        result = await session.execute(select(GridOperator))
        operators = result.scalars().all()
        return [PowerTariffRepository.operator_as_spec(op) for op in operators]

    @with_session
    async def list_power_tariffs(self, session: AsyncSession) -> list[PowerTariffSpec]:
        """Fetches all power tariffs with their associated metering grid areas."""

        result = await session.execute(
            select(PowerTariff)
            .options(
                # Load the many-to-many relationship with MeteringGridArea
                selectinload(PowerTariff.metering_grid_areas).selectinload(
                    MeteringGridArea.grid_operator
                )  # Also load the grid operator for each MGA
            )
            .options(
                # If you need the association objects with voltage info, load them too
                selectinload(PowerTariff.mga_associations)
                .selectinload(MeteringAreaByPowerTariffs.metering_grid_area)
                .selectinload(MeteringGridArea.grid_operator)
            )
        )

        power_tariffs = result.scalars().all()

        return [PowerTariffRepository.power_tariff_to_spec(tariff) for tariff in  power_tariffs]

    @with_session
    async def fetch_power_tariff_by_provider_name(self, provider_name:str, session:AsyncSession) -> PowerTariffSpec:
        """Fetches all power tariffs for a given provider."""
        # TODO find a better way to link providers comming from elomraden
        result = await session.execute(
            select(GridOperator)
            .where(GridOperator.name.startswith(provider_name.split()[0]))
            .options(
                selectinload(GridOperator.power_tariff).
                selectinload(PowerTariff.fees).
                selectinload(PowerTariffFee.compositions)
            )
        )
        provider = result.scalars().one_or_none()
        if provider is None:
            raise UnexpectedValue(f"Provider with name {provider_name} without power tariff definition.")
        return provider.power_tariff.as_spec()

    @with_session
    async def fetch_power_tariff_by_ediel(self, ediel:int, session:AsyncSession) -> PowerTariffSpec:
        """Fetches all power tariffs for a given provider."""
        result = await session.execute(
            select(GridOperator)
            .where(GridOperator.ediel == ediel)
            .options(
                selectinload(GridOperator.power_tariff).
                selectinload(PowerTariff.fees).
                selectinload(PowerTariffFee.compositions)
            )
        )
        provider  = result.scalars().one_or_none()
        if provider is None:
            raise UnexpectedValue(f"Provider with ediel {ediel} without power tariff definition.")
        return provider.power_tariff.as_spec()

    @with_session
    async def save_power_tariff(self, power_tariff:PowerTariffSpec, session:AsyncSession) -> PowerTariffSpec:
        # """Saves a power tariff to the database."""
        # provider = GridOperator(active=True, **power_tariff.provider.model_dump())
        # session.add(provider)
        # await session.flush()
        #
        # tariff = PowerTariff(
        #     **power_tariff.model_dump(exclude={"provider", "fees"}),
        #     provider_uid=provider.uid,
        # )
        # session.add(tariff)
        # await session.flush()
        #
        # # Create fees
        # for fee_data in power_tariff.fees:
        #     fee = PowerTariffFee(
        #         **fee_data.model_dump(exclude={"composition"}), tariff_id=tariff.uid
        #     )
        #     session.add(fee)
        #     await session.flush()  # Flush to get the fee UUID
        #
        #     # Now create compositions
        #     for comp_data in fee_data.compositions:
        #         composition = TariffComposition(
        #             **comp_data.model_dump(exclude={"fee"}), fee_id=fee.uid
        #         )
        #         session.add(composition)
        #
        # await session.commit()
        # return power_tariff
        pass

    @with_session
    async def save_operator(self, operator:GridOperatorSpec, session:AsyncSession) -> GridOperatorSpec:
        """Saves a grid operator to the database."""
        db_operator = PowerTariffRepository.operator_from_spec(operator)

        session.add(db_operator)
        return PowerTariffRepository.operator_as_spec(db_operator)

    @with_session
    async def get_operator(self, uid:UUID, session:AsyncSession) -> GridOperatorSpec | None:
        """Get a specific provider by its UUID."""
        result = await session.execute(
            select(GridOperator).where(GridOperator.uid == uid)
        )
        operator = result.scalars().one_or_none()
        if operator is not None:
            return PowerTariffRepository.operator_as_spec(operator)
        else:
            operator

    @with_session
    async def get_operator_by_ediel(self, ediel:int, session:AsyncSession) -> GridOperatorSpec | None:
        """Get a specific provider by its ediel id."""
        result = await session.execute(
            select(GridOperator).where(GridOperator.ediel == ediel)
        )
        operator = result.scalars().one_or_none()
        if operator is not None:
            return PowerTariffRepository.operator_as_spec(operator)
        else:
            return operator

    @with_session
    async def get_operator_by_name(self, name:str, session:AsyncSession) -> GridOperatorSpec | None:
        """Get a specific provider by its name."""
        result = await session.execute(
            select(GridOperator).where(name == GridOperator.name)
        )
        operator = result.scalars().one_or_none()
        if operator is not None:
            return PowerTariffRepository.operator_as_spec(operator)
        else:
            return operator

    @with_session
    async def get_metering_grid_area_by_code(self, code:str, session:AsyncSession):
        """Get a specific metering grid area by its code."""
        from repositories.orm_model import MeteringGridArea

        result = await session.execute(
            select(MeteringGridArea).where(MeteringGridArea.code == code)
        )
        area = result.scalars().one_or_none()
        return area

    @with_session
    async def save_metering_grid_area(self, mga:MeteringGridAreaSpec, session:AsyncSession) -> MeteringGridAreaSpec:
        """Saves a metering grid area to the database."""
        grid_operator = self.get_operator_by_name()
        db_mga = PowerTariffRepository.mga_from_spec(mga)
        session.add(db_mga)
        await session.commit()
        await session.refresh(db_mga,['grid_operator'])
        return PowerTariffRepository.mga_to_spec(db_mga)

    @staticmethod
    def operator_as_spec(grid_operator:GridOperator) -> GridOperatorSpec:
        """Converts a GridOperator ORM object to a GridOperatorSpec."""
        return GridOperatorSpec(
            uid=str(grid_operator.uid),
            name=grid_operator.name,
            ediel=grid_operator.ediel
        )

    @staticmethod
    def operator_from_spec(spec: GridOperatorSpec) -> GridOperator:
        """Converts a GridOperatorSpec to a GridOperator ORM object."""
        return GridOperator(
            uid = uuid.uuid7(),
            name=spec.name,
            ediel=spec.ediel
        )

    @staticmethod
    def mga_from_spec(mga:MeteringGridAreaSpec) -> MeteringGridArea:
        return MeteringGridArea(
            code=mga.code,
            name=mga.name,
            country_code=mga.country_code,
            metering_business_area=mga.metering_business_area,
            grid_operator_uid=UUID(mga.grid_operator.uid) if mga.grid_operator and mga.grid_operator.uid else None,
        )

    @staticmethod
    def mga_to_spec(mga:MeteringGridArea) -> MeteringGridAreaSpec:
        operator_spec:GridOperatorSpec = PowerTariffRepository.operator_as_spec(mga.grid_operator) if mga.grid_operator else None
        return MeteringGridAreaSpec(
            code=mga.code,
            name=mga.name,
            countryCode=mga.country_code,
            meteringBusinessArea=mga.metering_business_area,
            gridOperator= operator_spec.model_dump() if operator_spec else None
        )

    @staticmethod
    def power_tariff_to_spec(power_tariff:PowerTariff) -> PowerTariffSpec:
        mgas = power_tariff.metering_grid_areas
        tariff_spec = PowerTariffSpec(
            uid=str(power_tariff.uid),
            name=power_tariff.name,
            model=power_tariff.model,
            description=power_tariff.description,
            samplesPerMonth=power_tariff.samples_per_month,
            timeUnit=power_tariff.time_unit,
            isApartment=power_tariff.isApartment,
            lastUpdated=power_tariff.last_updated,
            validFrom=power_tariff.valid_from,
            validTo=power_tariff.valid_to,
            compositions=power_tariff.compositions,

        )
        return tariff_spec


repository = PowerTariffRepository()
