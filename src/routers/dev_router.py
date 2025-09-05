from engrate_sdk.utils import log
from fastapi import APIRouter

import env
from clients import elomraden_model, elomraden
from model import GridOperatorSpec
from utils import PowerTariffSvc

logger = log.get_logger(__name__)
router = APIRouter(
    tags=["Power Tariffs API"], include_in_schema=env.is_dev_mode(), prefix="/dev"
)


@router.get(
    "/areas/postal-code",
    response_model=elomraden_model.GridArea,
    summary="Returns a grid area by postal code",
)
async def fetch_area_by_postal_code(code: int):
    """Fetch an area by post code"""
    area = await elomraden.get_area_by_postnumber(code)
    return area


@router.get(
    "/areas/address",
    response_model=elomraden_model.GridArea,
    summary="Returns a grid area by address and locality",
)
async def fetch_area_by_address(address: str, locality: str):
    """Fetch an area by post code"""
    area = await elomraden.get_area_by_address(address, locality)
    return area


@router.get(
    "/areas/coordinates",
    response_model=elomraden_model.GridArea,
    summary="Returns a grid area by coordinates",
)
async def fetch_area_by_coordinates(lat: str, lon: str):
    """Fetch an area by coordinates"""
    area = await elomraden.get_area_by_coordinates(lat, lon)
    return area


@router.get(
    "/grid-operators",
    response_model=list[GridOperatorSpec],
    summary="Returns all grid operators",
)
async def fetch_grid_operators(power_tariffs_service: PowerTariffSvc):
    """Fetches all grid operators."""
    return await power_tariffs_service.get_grid_operators()
