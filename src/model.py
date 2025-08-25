from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class TimeIntervalSpec(BaseModel):
    """Time interval for tariff rates. Multiplier is necessary given companies might have different rates per interval"""
    from_time: str = Field(..., alias="from")
    to_time: str = Field(..., alias="to")
    multiplier: float

    class Config:
        populate_by_name = True

class TariffCompositionSpec(BaseModel):
    """Component of a tariff fee composition"""
    months: list[int]
    days: list[str]
    fuse_from: str = Field(..., alias="fuseFrom")
    fuse_to: str = Field(..., alias="fuseTo")
    hints: dict
    unit: str
    price_exc_vat: float = Field(..., alias="priceExcVat")
    price_inc_vat: float = Field(..., alias="priceIncVat")
    intervals: list[TimeIntervalSpec]

    class Config:
        populate_by_name = True

class BuildingTypeSpec(str, Enum):
    DETACHED_HOUSE = "detached_house"
    TERRACED_HOUSE = "terraced_house"
    SUMMER_HOUSE = "summer_house"
    APARTMENTS = "apartments"

class PowerTariffFeeSpec(BaseModel):
    """Power tariff fee structure"""
    name: str
    model: str
    description: str
    samples_per_month: int = Field(..., alias="samplesPerMonth")
    time_unit: str = Field(..., alias="timeUnit")
    building_types: List[BuildingTypeSpec] = Field(..., alias="buildingTypes")
    composition: list[TariffCompositionSpec]

    class Config:
        populate_by_name = True

class GridProviderSpec(BaseModel):
    """Grid provider model for a DSO"""
    uid: str
    name: str
    ediel: int
    org_number: str


class PowerTariffSpec(BaseModel):
    """Power tariff model for a DSO"""
    id: str
    provider: GridProviderSpec
    country_code: str = Field(..., alias="countryCode")
    time_zone: str = Field(..., alias="timeZone")
    last_updated: datetime = Field(..., alias="lastUpdated")
    valid_from: datetime = Field(..., alias="validFrom")
    valid_to: datetime = Field(..., alias="validTo")
    fees: list[PowerTariffFeeSpec]

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

