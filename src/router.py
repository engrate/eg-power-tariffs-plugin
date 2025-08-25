from typing import Annotated

from fastapi import APIRouter, Depends

from engrate_sdk.utils import log
from src.clients import elomraden_model, elomraden
from src.model import GridProviderSpec, PowerTariffSpec
from src.power_tariff_service import PowerTariffService
from src.repositories.powtar_repository import PowerTariffRepository

logger = log.get_logger(__name__)
router = APIRouter(
    tags=["Power Tariffs API"],
    include_in_schema=True,
    prefix="/v1/plugins/power-tariffs"
)

PowerTariffSvc = Annotated[PowerTariffService, Depends(lambda: PowerTariffService(repository=PowerTariffRepository()))]

@router.get("/areas/postal-code",
            response_model=elomraden_model.GridArea,
            summary="Returns a grid area by postal code",
            include_in_schema=True)
async def fetch_area_by_postal_code(code:int):
    """Fetch an area by post code"""
    area = await elomraden.get_area_by_postnumber(code)
    return area

@router.get("/areas/address",
            response_model=elomraden_model.GridArea,
            summary="Returns a grid area by address and locality",
            include_in_schema=True)
async def fetch_area_by_address(address:str, locality:str):
    """Fetch an area by post code"""
    area = await elomraden.get_area_by_address(address,locality)
    return area

@router.get("/areas/coordinates",
            response_model=elomraden_model.GridArea,
            summary="Returns a grid area by coordinates",
            include_in_schema=True)
async def fetch_area_by_coordinates(lat:str, lon:str):
    """Fetch an area by coordinates"""
    area = await elomraden.get_area_by_coordinates(lat,lon)
    return area

@router.get("/providers",
            response_model=list[GridProviderSpec],
            summary="Returns all grid providers",
            include_in_schema=True)
async def fetch_grid_providers(power_tariffs_service: PowerTariffSvc):
    """Fetches all grid providers."""
    return await power_tariffs_service.get_grid_providers()

@router.get("/",
            response_model=list[PowerTariffSpec],
            summary="Returns all power tariffs definitions",
            include_in_schema=True)
async def power_tariffs(power_tariffs_service: PowerTariffSvc):
    """Fetches all power tariffs definitions."""
    rs =  await power_tariffs_service.get_tariffs()
    return rs

@router.get("/address",
            response_model=PowerTariffSpec,
            summary="Returns power tariffs by address",
            include_in_schema=True)
async def power_tariff_by_address(power_tariffs_service: PowerTariffSvc, address:str, ort:str):
    """Fetches power tariffs by address."""
    return await power_tariffs_service.get_tariff_by_address(address,ort)

@router.get("/postal-code",
            response_model=PowerTariffSpec,
            summary="Returns power tariffs by postal code",
            include_in_schema=True)
async def power_tariff_by_postal_code(power_tariffs_service: PowerTariffSvc, code:int):
    """Fetches power tariffs by postal code."""
    return await power_tariffs_service.get_tariff_by_postal_code(code)
