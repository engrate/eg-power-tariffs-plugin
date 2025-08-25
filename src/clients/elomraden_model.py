from enum import Enum
from typing import Optional

from pydantic import BaseModel

from src.exceptions import UnexpectedValue

class AdditionalDetails(BaseModel):
    municipality:str
    energy_tax:bool
    energy_tax_name:str
    locality:Optional[str]


class GridCompany(BaseModel):
    name:str
    ediel:int
    email:str
    phone:str

class Zone(Enum):
    SE1 = 1
    SE2 = 2
    SE3 = 3
    SE4 = 4

class GridArea(BaseModel):
    area_name: str
    area_code:str
    zone:Zone
    company:GridCompany
    additional_details: Optional[AdditionalDetails]

def zone_from_code(code:int) -> Zone:
    """Converts an int to a Zones enum."""
    for zone in Zone:
        if zone.value == code:
            return zone.name
    raise UnexpectedValue(f"Invalid zone number: {code}. Expected 1, 2, 3, or 4")
