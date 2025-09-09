from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field, BaseModel


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class Spec(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True


class BuildingType(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    ALL = "all"


class TimeIntervalSpec(Spec):
    """Time interval for tariff rates. Multiplier is necessary given companies might have different rates per interval"""

    from_time: str = Field(..., alias="from")
    to_time: str = Field(..., alias="to")
    multiplier: float

    class Config:
        populate_by_name = True


class TariffCompositionSpec(Spec):
    """Component of a tariff fee composition"""

    months: list[str]
    days: list[str]
    fuse_from: str = Field(...)
    fuse_to: str = Field(...)
    unit: str
    price_exc_vat: float = Field(...)
    price_inc_vat: float = Field(...)
    intervals: list[TimeIntervalSpec]

    class Config:
        populate_by_name = True


class PowerTariffSpec(Spec):
    """Power tariff model for a DSO - now includes fee information directly"""

    uid: Optional[str] = None
    name: str
    model: str
    description: Optional[str] = None
    samples_per_month: int = Field(...)
    time_unit: str = Field(...)
    building_type: BuildingType = Field(default="all")
    last_updated: datetime = Field(...)
    valid_from: Optional[datetime] = Field(default=None)
    valid_to: Optional[datetime] = Field(default=None)
    voltage: str
    compositions: list[TariffCompositionSpec]
    metering_grid_areas: list["MeteringGridAreaSpec"]

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class GridOperatorSpec(Spec):
    """Grid provider model for a DSO"""

    uid: Optional[str] = None
    name: str
    ediel: int

    class Config:
        populate_by_name = True


class MeteringGridAreaSpec(Spec):
    """Metering grid area model for a DSO"""

    code: str
    name: str
    country_code: str = Field(default="SE")
    metering_business_area: str = Field(...)
    grid_operator: GridOperatorSpec = Field(...)
    power_tariffs: Optional[list[PowerTariffSpec]] = Field(default=None)

    class Config:
        populate_by_name = True
