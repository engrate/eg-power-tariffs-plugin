from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UUID,
    ForeignKey,
    Text,
    func,
    JSON,
    MetaData,
)
from sqlalchemy.orm import relationship, declarative_base, Mapped

from engrate_sdk.utils.uuid import uuid7

BaseSQLModel = declarative_base()
metadata = MetaData()


class GridOperator(BaseSQLModel):
    __tablename__ = "grid_operators"

    uid = Column(UUID, primary_key=True, default=uuid7)
    name = Column(String, nullable=False, unique=True)
    ediel = Column(Integer, nullable=False, unique=True)
    metering_grid_areas: Mapped[list["MeteringGridArea"]] = relationship(
        "MeteringGridArea", back_populates="grid_operator", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<GridProvider(id={self.uid}, name='{self.name}')>"


class PowerTariff(BaseSQLModel):
    __tablename__ = "power_tariffs"

    uid = Column(UUID, primary_key=True, default=uuid7)
    name = Column(String(255), nullable=False)
    model = Column(String(50), nullable=False)
    description = Column(Text)
    samples_per_month = Column(Integer, nullable=False)
    time_unit = Column(String(20), nullable=False)
    building_type = Column(String(50), nullable=False, default=False)
    last_updated = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_to = Column(DateTime(timezone=True), nullable=True)
    voltage = Column(String(10), nullable=False)
    compositions = Column(JSON, nullable=False)

    metering_grid_areas: Mapped[list["MeteringGridArea"]] = relationship(
        "MeteringGridArea",
        secondary="metering_grid_area_x_power_tariff",
        back_populates="power_tariffs",
        viewonly=True,
    )

    mga_associations: Mapped[list["MeteringGridAreaByPowerTariffs"]] = relationship(
        "MeteringGridAreaByPowerTariffs",
        back_populates="power_tariff",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<PowerTariff(id={self.uid}, name='{self.name}')>"


class MeteringGridArea(BaseSQLModel):
    __tablename__ = "metering_grid_areas"

    code: Column[str] = Column(String(50), primary_key=True, unique=True)
    name = Column(String(255), nullable=False, unique=True)
    country_code = Column(String(5), nullable=False, unique=False, default="SE")
    metering_business_area = Column(String(5), nullable=False, unique=False)
    grid_operator_uid = Column(UUID, ForeignKey("grid_operators.uid"), nullable=True)
    grid_operator: Mapped["GridOperator"] = relationship(
        "GridOperator", back_populates="metering_grid_areas", uselist=False
    )

    power_tariffs: Mapped[list["PowerTariff"]] = relationship(
        "PowerTariff",
        secondary="metering_grid_area_x_power_tariff",
        back_populates="metering_grid_areas",
        viewonly=True,
    )

    tariff_associations: Mapped[list["MeteringGridAreaByPowerTariffs"]] = relationship(
        "MeteringGridAreaByPowerTariffs",
        back_populates="metering_grid_area",
        cascade="all, delete-orphan",
    )


def __repr__(self):
    return f"<MeteringGridArea(code={self.code}, name='{self.name}')>"


class MeteringGridAreaByPowerTariffs(BaseSQLModel):
    __tablename__ = "metering_grid_area_x_power_tariff"

    uid = Column(UUID, primary_key=True, default=uuid7)
    mga_code = Column(String(5), ForeignKey("metering_grid_areas.code"), nullable=False)
    tariff_uid = Column(UUID, ForeignKey("power_tariffs.uid"), nullable=False)
    metering_grid_area: Mapped["MeteringGridArea"] = relationship(
        "MeteringGridArea", back_populates="tariff_associations"
    )
    power_tariff: Mapped["PowerTariff"] = relationship(
        "PowerTariff", back_populates="mga_associations"
    )

    def __repr__(self):
        return f"<MeteringAreaByPowerTariffs(uid={self.uid}, mga_code='{self.mga_code}', tariff_uid='{self.tariff_uid}')>"
