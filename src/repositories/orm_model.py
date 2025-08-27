from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    UUID,
    ForeignKey,
    Text,
    ARRAY,
    func,
    JSON,
    MetaData,
    Boolean,
)
from sqlalchemy.orm import relationship, declarative_base, Mapped

from engrate_sdk.utils.uuid import uuid7
from src.model import (
    GridProviderSpec,
    PowerTariffSpec,
    PowerTariffFeeSpec,
    TariffCompositionSpec,
    TimeIntervalSpec,
)

BaseSQLModel = declarative_base()
metadata = MetaData()

class TariffComposition(BaseSQLModel):
    __tablename__ = "tariff_compositions"

    uid = Column(UUID, primary_key=True, default=uuid7)
    fee_id = Column(UUID, ForeignKey("power_tariff_fees.uid"), nullable=False)
    months = Column(ARRAY(Integer), nullable=False)
    days = Column(ARRAY(String), nullable=False)
    fuse_from = Column(String(10), nullable=False)
    fuse_to = Column(String(10), nullable=False)
    hints = Column(JSON)
    unit = Column(String(20), nullable=False)
    price_exc_vat = Column(Float, nullable=False)
    price_inc_vat = Column(Float, nullable=False)
    intervals = Column(JSON, nullable=False)
    fee = relationship("PowerTariffFee", back_populates="compositions")
    def __repr__(self):
        return f"<TariffComposition(id={self.uid}, hints={self.hints})>"

class PowerTariffFee(BaseSQLModel):
    __tablename__ = "power_tariff_fees"

    uid = Column(UUID, primary_key=True, default=uuid7)
    tariff_id = Column(UUID, ForeignKey("power_tariffs.uid"), nullable=False)
    name = Column(String(255), nullable=False)
    model = Column(String(50), nullable=False)
    description = Column(Text)
    samples_per_month = Column(Integer, nullable=False)
    time_unit = Column(String(20), nullable=False)
    building_types = Column(ARRAY(String(50)))
    tariff = relationship("PowerTariff", back_populates="fees",lazy="subquery")
    compositions:Mapped[list[TariffComposition]] = relationship("TariffComposition", back_populates="fee", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PowerTariffFee(id={self.uid}, name='{self.name}')>"

class GridProvider(BaseSQLModel):
    __tablename__ = "providers"

    uid = Column(UUID, primary_key=True, default=uuid7)
    name = Column(String, nullable=False, unique=True)
    ediel = Column(Integer, nullable=False, unique=True)
    org_number = Column(String(50), nullable=False, unique=True)
    active = Column(Boolean, nullable=False, unique=False)
    power_tariff = relationship("PowerTariff", back_populates="provider", lazy="subquery", uselist=False )

    def __repr__(self):
        return f"<GridProvider(id={self.uid}, name='{self.name}')>"

    def as_spec(self) -> GridProviderSpec:
        return GridProviderSpec(
                uid=str(self.uid),
                name=self.name,
                ediel=self.ediel,
                org_number=self.org_number
        )


class PowerTariff(BaseSQLModel):
    __tablename__ = "power_tariffs"

    uid = Column(UUID, primary_key=True, default=uuid7)
    provider_uid: UUID = Column(UUID, ForeignKey("providers.uid"), nullable=False)
    country_code = Column(String(5), nullable=False, unique=True)
    time_zone = Column(String(50), nullable=False, unique=False, default="Europe/Stockholm")
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_to = Column(DateTime(timezone=True), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fees:Mapped[list[PowerTariffFee]]= relationship("PowerTariffFee", back_populates="tariff", cascade="all, delete-orphan")
    provider:Mapped[GridProvider]= relationship("GridProvider",back_populates="power_tariff", uselist=False)
    def __repr__(self):
        return f"<PowerTariff(id={self.uid}, name='{self.name}')>"

    def as_spec(self) -> PowerTariffSpec:
        # Create the main tariff
        tariff_spec = PowerTariffSpec(
            id=str(self.uid),
            provider=self.provider.as_spec(),
            countryCode=self.country_code,
            timeZone=self.time_zone,
            lastUpdated=self.last_updated,
            validFrom=self.valid_from,
            validTo=self.valid_to,
            fees=[],
        )

        for fee_data in self.fees:
            fee = PowerTariffFeeSpec(
                name=fee_data.name,
                model=fee_data.model,
                description=fee_data.description,
                samplesPerMonth=fee_data.samples_per_month,
                timeUnit=fee_data.time_unit,
                buildingTypes=fee_data.building_types,
                composition=[],
            )
            tariff_spec.fees.append(fee)


            for comp_data in fee_data.compositions:
                #build intervals
                interval_specs = []
                if comp_data.intervals:
                    for interval_dict in comp_data.intervals:
                        interval_spec = TimeIntervalSpec(
                            from_time=interval_dict.get("from", ""),
                            to=interval_dict.get("to", ""),
                            multiplier=interval_dict.get("multiplier", 1.0),
                        )
                        interval_specs.append(interval_spec)

                #build hints
                hints_dict = {
                        hint["type"]: hint["value"]
                        for hint in (comp_data.hints or [])
                        if isinstance(hint, dict) and "type" in hint and "value" in hint
                }
                
                comp = TariffCompositionSpec(
                    months=comp_data.months,
                    days=comp_data.days,
                    fuseFrom=comp_data.fuse_from,
                    fuseTo=comp_data.fuse_to,
                    hints=hints_dict,
                    unit=comp_data.unit,
                    priceExcVat=comp_data.price_exc_vat,
                    priceIncVat=comp_data.price_inc_vat,
                    intervals=interval_specs
                )
                fee.composition.append(comp)

        return tariff_spec

