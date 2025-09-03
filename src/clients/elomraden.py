from enum import Enum

from engrate_sdk.utils import log
from engrate_sdk.http.client import AsyncClient
from src import env
from .elomraden_model import GridCompany, AdditionalDetails, GridArea
from src.exceptions import (
    NotEnabledError,
    IllegalArgumentError,
    UnknownError,
    MissingError,
)

__BASE_LOOKUP_URL = env.get_elomraden_base_url()
__AUTH_SUFFIX = f"user/{env.get_elomraden_user()}/key/{env.get_elomraden_apikey()}"

logger = log.get_logger(__name__)

## Types ##
class ResponseFormat(Enum):
    JSON = "json"
    XML = "xml"

async def get_area_by_address(address:str, ort:str) -> GridArea:
    """Gets an electricity area by address."""
    async with AsyncClient() as client:
        resp = await client.get(__address_lookup_path(address, ort))
        resp.raise_for_status()
        data = resp.json()
        print(data)
        # Check biz errors
        area_data = data.get("elomradeAdress", {})
        if area_data.get("success") != 1:
            error = area_data.get("error", {})
            __handle_error_response(error, "latitude:{lat}, longitude:{lon}")

        elnat = area_data.get("elnat", {})
        geo = area_data.get("geografi", {})
        # Map the fields from the API response to our model
        grid_area = GridArea(
            area_name=elnat.get("natomradeNamn", ""),
            area_code=elnat.get("natomradeBeteckning", 0),
            zone=elnat.get("elomrade", 0),
            company=GridCompany(
                name=elnat.get("natagare", ""),
                ediel=elnat.get("EdielID", ""),
                email=elnat.get("epost", ""),
                phone=elnat.get("telefon", ""),
            ),
            additional_details=AdditionalDetails(
                municipality=geo.get("kommun", ""),
                energy_tax=geo.get("elskatt", False),
                energy_tax_name=geo.get("elskattNamn", ""),
                locality=geo.get("ort", ""),
            ),
        )

        return grid_area

async def get_area_by_postnumber(postnumber:int) -> GridArea:
    """Gets an electricity area by postnumber."""

    async with AsyncClient() as client:
        resp = await client.get(__postcode_lookup_path(postnumber))
        resp.raise_for_status()
        data = resp.json()
        # Check biz errors
        pnr_data = data.get("natomradePostnummer", {})
        if pnr_data.get("success") != 1:
            error = pnr_data.get("error", {})
            __handle_error_response(error,postnumber)
        print(data)
        items = pnr_data.get("item", []) #TODO treat this as an array
        if not items:
            ##Not sure if this is possible though
            logger.warning(f"No grid area information found in the response for postnumber {postnumber}")
            return None
        print(f'items: {len(items)}')
        item = items[0]
        elnat = item.get("elnat", {})
        geo = item.get("geografi", {})
        # Map the fields from the API response to our model
        grid_area = GridArea(
            area_name=elnat.get("natomradeNamn", ""),
            area_code=elnat.get("natomradeBeteckning", 0),
            zone=elnat.get("elomrade", 0),
            company=GridCompany(
                name=elnat.get("natagare", ""),
                ediel=elnat.get("EdielID", ""),
                email=elnat.get("epost", ""),
                phone=elnat.get("telefon", ""),
            ),
            additional_details=AdditionalDetails(
                municipality=geo.get("kommun", ""),
                energy_tax=geo.get("elskatt", False),
                energy_tax_name=geo.get("elskattNamn", ""),
                locality=geo.get("ort", ""),
            ),
        )

        return grid_area

async def get_area_by_coordinates(lat:str, lon:str) -> GridArea:
    """Gets an electricity area by coordinates."""
    async with AsyncClient() as client:
        resp = await client.get(__coordinates_lookup_path(lat, lon))
        resp.raise_for_status()
        data = resp.json()
        # Check biz errors
        area_data = data.get("elomradeAdress", {}) ## Unfortunately the json atts have different names for the same value depending on the endpoint
        if area_data.get("success") != 1:
            error = area_data.get("error", {})
            __handle_error_response(error, "latitude:{lat}, longitude:{lon}")

        elnat = area_data.get("elnat", {})
        geo = area_data.get("geografi", {})
        # Map the fields from the API response to our model
        grid_area = GridArea(
            area_name=elnat.get("natomradeNamn", ""),
            area_code=elnat.get("natomradeBeteckning", 0),
            zone=elnat.get("elomrade", 0),
            company=GridCompany(
                name=elnat.get("natagare", ""),
                ediel=elnat.get("EdielID", ""),
                email=elnat.get("epost", ""),
                phone=elnat.get("telefon", ""),
            ),
            additional_details=AdditionalDetails(
                municipality=geo.get("kommun", ""),
                energy_tax=geo.get("elskatt", False),
                energy_tax_name=geo.get("elskattNamn", ""),
                locality=geo.get("ort", ""),
            ),
        )

        return grid_area

async def get_area_information(area:str) -> GridCompany:
    """Gets information about an electricity area."""
    async with AsyncClient() as client:
        resp = await client.get(__area_lookup_path(area))
        resp.raise_for_status()
        data = resp.json()
        # Check biz errors
        if data.get("success") != 1:
            error = data.get("error", {})
            __handle_error_response(error, area)

        _input = data.get('input',{})
        omrade= data.get('omrade',{})

        # Map the fields from the API response to our model
        grid_area = GridArea(
            area_name=omrade.get("namn", ""),
            area_code= _input.get('omrade', ""),
            zone=int(omrade.get("snitt", 0)),
            company=GridCompany(
                name=omrade.get("bolag", ""),
                ediel=omrade.get("bolagkod", 0),
                email=omrade.get("epost", ""),
                phone=omrade.get("telefon", ""),
            ),
        )
        return grid_area

def __postcode_lookup_path(postnumber:int, output: ResponseFormat = ResponseFormat.JSON.value) -> str:
    return f"{__BASE_LOOKUP_URL}/postnr/postnummer/{postnumber}/output/{output}/{__AUTH_SUFFIX}"

def __address_lookup_path(street:str, ort:str, output: ResponseFormat = ResponseFormat.JSON) -> str:
    return f"{__BASE_LOOKUP_URL}/adress/adress/{street}/ort/{ort}/output/{output.value}/{__AUTH_SUFFIX}"

def __coordinates_lookup_path(lat:float, lon:float, output: ResponseFormat = ResponseFormat.JSON) -> str:
    return f"{__BASE_LOOKUP_URL}/koord/latitud/{lat}/longitud/{lon}/output/{output.value}/{__AUTH_SUFFIX}"

def __area_lookup_path(area:str, output: ResponseFormat = ResponseFormat.JSON) -> str:
    return f"{__BASE_LOOKUP_URL}/natomrade/omrade/{area}/output/{output.value}/{__AUTH_SUFFIX}"

def __handle_error_response(error,arg):
    """Handles error responses from the API."""
    err_code = error.get("errorCode", 0)
    err_msg = error.get("errorString", "Unknown error")
    if err_code == 2:
        logger.error(f"Area not found for argument {arg}: [{err_code}]{err_msg} ")
        raise MissingError("post number", str(arg))
    if err_code == 99:
        raise UnknownError("Unknown error", str(err_code), err_msg)
    if err_code == 90:
        logger.error("API not enabled: [{err_code}]:{err_msg} ")
        raise NotEnabledError("API method or operation not enabled")
    if err_code == 1:
        ##I couldn't reproduce this one, it's returning a 403
        logger.error(f"Wrong : [{err_code}]:{err_msg} ")
        raise IllegalArgumentError()
