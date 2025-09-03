import os
from contextlib import asynccontextmanager
from http import HTTPStatus

from engrate_sdk.core.registry import PluginRegistry
from engrate_sdk.types.exceptions import ParseError, ValidationError, AlreadyExistsError
from engrate_sdk.utils import log
from engrate_sdk.utils.uuid import uuid7
from fastapi import FastAPI
from fastapi import Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from httpx import HTTPStatusError, ConnectError
from sqlalchemy.exc import IntegrityError
from starlette.middleware.cors import CORSMiddleware

import src.db as db
from model import PowerTariffSpec, GridOperatorSpec, MeteringGridAreaSpec
from repositories.orm_model import GridOperator, MeteringGridArea
from src import env
import src.exceptions as ex
from src.exceptions import IllegalStateError
from src.router import router
from src import app
from src.repositories.power_tariffs_repository import repository

logger = log.get_logger(__name__)

async def _init_plugin() -> int | None:
    """Initializes the plugin."""
    try:
        env.validate()
        if not env.get_auto_register():
            logger.info("Auto registration is disabled, skipping plugin registration.")
            return None
        logger.info("Auto registration is enabled, registering plugin...")
        plugin_registry = PluginRegistry(env.get_registrar_url())
        await plugin_registry.register_plugin()
        logger.info("Plugin power tariffs registered successfully.")

    except ConnectError as e:
        logger.error(
            f"Failed to register plugin: {e} - Registar not available at {env.get_registrar_url()}. "
        )

    except (ParseError, ValidationError) as e:
        raise IllegalStateError(
            f"Failed to register plugin. Error while parsing manifest file: {e}"
        )
    except AlreadyExistsError as e:
        logger.warning(f"Plugin already registered, skipping: {e}")
    except Exception as e:
        raise IllegalStateError(f"Failed to register plugin: {e}")


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    """Startup and shutdown logic using lifespan events."""
    try:
        if env.get_auto_register():
            logger.info("Registering plugin...")
            await _init_plugin()

        logger.info("Initializing database connection...")
        fast_app.state.db = await db.start()
        await db.await_up(fast_app.state.db)
        logger.info("Database connection established.")

        if env.must_load_tariffs_definitions():
            await load_tariffs_definitions()
        if env.must_load_operators():
            await load_grid_operators()
        if env.must_load_metering_grid_areas():
            await load_metering_grid_areas()
        yield
    finally:
        logger.info("Shutting down power tariffs plugin...")
        if fast_app.state.db:
            logger.info("Closing database connection...")
            await db.stop(fast_app.state.db)


async def load_tariffs_definitions():
    import json
    from pathlib import Path
    for file_path in Path("data/power-tariffs").glob("*.json"):
        with open(file_path, "r") as f:
            data = json.load(f)
            spec = PowerTariffSpec(**data)
            try:
                await repository.save_power_tariff(spec)
                logger.info(f"Loaded tariff definition from {file_path}")
            except IntegrityError:
                logger.warning(f"Tariff definition from {file_path} already exists, skipping.")

async def load_grid_operators():
    from pathlib import Path
    import csv

    with open(Path("data/operators/operators.csv"), "r", encoding="utf-8") as file:

        reader = csv.reader(file)
        for row in reader:
            if len(row) < 7:
                logger.warning(f"Skipping malformed row: {row}")
                continue

            # Extract fields
            status = row[0].strip()
            name = row[1].strip()
            ediel_id = row[3].strip()

            # Skip if not a grid operator (Nätägare)
            if "Godkänd" not in status:
                logger.warning(f"Skipping {name} - operator not approved")
                continue

            # Check if operator already exists
            existing_operator = await repository.get_operator_by_ediel(int(ediel_id))
            if existing_operator:
                logger.warning(f"Operator {name} already exists, skipping")
                continue

            # Create new grid operator
            grid_operator = GridOperatorSpec(
                name=name,
                ediel=int(ediel_id),
            )

            await repository.save_operator(grid_operator)
            logger.info(
                f"Created grid operator: {name} (Ediel: {ediel_id})"
            )

async def load_metering_grid_areas():
    from pathlib import Path
    import csv

    with open(Path("data/metering_grid_areas/mgas.csv"), "r", encoding="utf-8") as file:
        reader = csv.reader(file,delimiter=";")
        for row in reader:
            if len(row) < 6:
                logger.warning(f"Skipping malformed row: {row}")
                continue

            # Extract fields
            operator_name = row[0].strip()
            mga_name = row[1].strip()
            mga_code = row[2].strip()
            mga_type = row[3].strip()
            mba_code = row[4].strip()
            country = row[5].strip()

            # Skip if not a grid operator (Nätägare)
            if "DISTRIBUTION" not in mga_type:
                logger.warning(f"Skipping {mga_name} - only DISTRIBUTION types are supported")
                continue

            # Check if operator already exists
            existing_operator = await repository.get_operator_by_name(operator_name)
            if not existing_operator:
                logger.warning(f"Operator {operator_name} does not exists, skipping")
                continue

            mag = MeteringGridAreaSpec(
                code=mga_code,
                countryCode=country,
                name=mga_name,
                meteringBusinessArea=mba_code,
                gridOperator=existing_operator.model_dump(),
            )
            existing_mga = await repository.get_metering_grid_area_by_code(mga_code)
            if existing_mga:
                logger.warning(f"Metering grid area {mga_code} already exists, skipping")
                continue
            await repository.save_metering_grid_area(mag)
            logger.info(f"Metering grid area saved: {mga_name} (Code: {mga_code})")

##Exception handlers###
@app.exception_handler(Exception)
async def global_exception_handler(request:Request,exc: Exception):
    logger.error(f"An unexpected error occurred: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )


@app.exception_handler(ex.MissingError)
async def missing_error_exception_handler(request:Request,exc: ex.MissingError):
    detail = f"{str(exc.kind).capitalize()} with ID {exc.id} not found"
    logger.error(f"Missing error: {detail}")
    return JSONResponse(
        status_code=404,
        content={"detail": detail},
    )


@app.exception_handler(HTTPStatusError)
async def wrong_credentials_error_handler(request:Request,exc: HTTPStatusError):
    if exc.response.status_code == 403:
        cause = "Forbidden"
    elif exc.response.status_code == 401:
        cause = "Unauthorized"
    else:
        cause = HTTPStatus(exc.response.status_code).phrase

    detail = f"Error: {str(cause)}"
    logger.error(detail)
    return JSONResponse(
        status_code=exc.response.status_code,
        content={"detail": detail},
    )


@app.exception_handler(ex.UnexpectedValue)
async def illegal_argument_error_handler(request:Request,exc: ex.UnexpectedValue):
    uid = uuid7()
    logger.error(f"Unexpected value error with ID {uid}:\n{exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.details},
    )


@app.exception_handler(ex.NotEnabledError)
async def not_enabled_error_handler(request:Request,exc: ex.NotEnabledError):
    uid = uuid7()
    logger.error(f"Operation not enabled error with ID {uid}:\n{exc}")
    return JSONResponse(
        status_code=501,
        content={"detail": "operation not enabled"},
    )


@app.exception_handler(ex.UnknownError)
async def unknown_error_exception_handler(request:Request,exc: ex.UnknownError):
    uid = uuid7()
    logger.error(f"Unknown error with ID {uid}:\n{exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"An unexpected error occurred, we're on it. Incident ID: {uid}"
        },
    )


def custom_openapi():
    """Customize the OpenAPI schema page."""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Power Tariffs Engrate API",
        version="0.1.0",
        summary="Provides information about different power tariffs schema by grid provider",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "http://localhost:3011/static/engrate_logo_white.png"  # TODO host
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
static_dir = os.path.join(parent_dir, "static")

app.openapi = custom_openapi
app.add_middleware(
    CORSMiddleware,
    allow_origins=env.get_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.router.lifespan_context = lifespan
app.include_router(router)
