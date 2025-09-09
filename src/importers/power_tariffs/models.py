from typing import List
from pydantic import BaseModel

from src.model import BuildingType


class Interval(BaseModel):
    from_time: str
    to_time: str
    multiplier: float


class PowerTariffComposition(BaseModel):
    months: List[str]
    days: List[str]
    fuse_from: str
    fuse_to: str
    unit: str
    price_exc_vat: float
    price_inc_vat: float
    intervals: List[Interval]


class PowerTariff(BaseModel):
    tariff_id: str
    name: str
    model: str
    description: str
    samples_per_month: int
    time_unit: str
    building_type: BuildingType
    mgas: list[str] = []
    tariff_composition: List[PowerTariffComposition]


class Operator(BaseModel):
    ediel: int
    power_tariffs: List[PowerTariff]
