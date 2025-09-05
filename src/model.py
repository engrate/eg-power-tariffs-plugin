from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BuildingType(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    ALL = "all"


class TimeIntervalSpec(BaseModel):
    """Time interval for tariff rates. Multiplier is necessary given companies might have different rates per interval"""

    from_time: str = Field(..., alias="from")
    to_time: str = Field(..., alias="to")
    multiplier: float

    class Config:
        populate_by_name = True


class TariffCompositionSpec(BaseModel):
    """Component of a tariff fee composition"""

    months: list[str]
    days: list[str]
    fuse_from: str = Field(..., alias="fuseFrom")
    fuse_to: str = Field(..., alias="fuseTo")
    unit: str
    price_exc_vat: float = Field(..., alias="priceExcVat")
    price_inc_vat: float = Field(..., alias="priceIncVat")
    intervals: list[TimeIntervalSpec]

    class Config:
        populate_by_name = True


class PowerTariffSpec(BaseModel):
    """Power tariff model for a DSO - now includes fee information directly"""

    uid: Optional[str] = None
    name: str
    model: str
    description: Optional[str] = None
    samples_per_month: int = Field(..., alias="samplesPerMonth")
    time_unit: str = Field(..., alias="timeUnit")
    building_type: BuildingType = Field(default="all", alias="buildingType")
    last_updated: datetime = Field(..., alias="lastUpdated")
    valid_from: Optional[datetime] = Field(default=None, alias="validFrom")
    valid_to: Optional[datetime] = Field(default=None, alias="validTo")
    voltage: str
    compositions: list[TariffCompositionSpec]
    metering_grid_areas: list["MeteringGridAreaSpec"]

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class GridOperatorSpec(BaseModel):
    """Grid provider model for a DSO"""

    uid: Optional[str] = None
    name: str
    ediel: int

    class Config:
        populate_by_name = True


class MeteringGridAreaSpec(BaseModel):
    """Metering grid area model for a DSO"""

    code: str
    name: str
    country_code: str = Field(default="SE", alias="countryCode")
    metering_business_area: str = Field(..., alias="meteringBusinessArea")
    grid_operator: GridOperatorSpec = Field(..., alias="gridOperator")
    power_tariffs: Optional[list[PowerTariffSpec]] = Field(default=None, alias="powerTariffs")

    class Config:
        populate_by_name = True
