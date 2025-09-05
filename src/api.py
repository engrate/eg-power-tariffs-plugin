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
from starlette.middleware.cors import CORSMiddleware

import src.db as db
import src.exceptions as ex
from src.routers.admin_router import router as admin_router
from src.routers.dev_router import router as dev_router
from src.routers.main_router import router as main_router
from src import app
from src import env
from src.exceptions import IllegalStateError

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

        await _init_db()
        yield
    finally:
        logger.info("Shutting down power tariffs plugin...")
        if fast_app.state.db:
            logger.info("Closing database connection...")
            await db.stop(fast_app.state.db)


async def _init_db():
    if env.must_load_operators():
        from src.importers.grid_operators_importer import load_grid_operators

        await load_grid_operators()
    if env.must_load_metering_grid_areas():
        from src.importers.metering_grid_areas_importer import (
            load_metering_grid_areas,
        )

        await load_metering_grid_areas()
    if env.must_load_tariffs_definitions():
        from src.importers.power_tariffs.importer import load_tariffs_definitions

        await load_tariffs_definitions()


##Exception handlers###
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"An unexpected error occurred: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )


@app.exception_handler(ex.MissingError)
async def missing_error_exception_handler(request: Request, exc: ex.MissingError):
    detail = f"{str(exc.kind).capitalize()} with ID {exc.id} not found"
    logger.error(f"Missing error: {detail}")
    return JSONResponse(
        status_code=404,
        content={"detail": detail},
    )


@app.exception_handler(HTTPStatusError)
async def wrong_credentials_error_handler(request: Request, exc: HTTPStatusError):
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
async def illegal_argument_error_handler(request: Request, exc: ex.UnexpectedValue):
    uid = uuid7()
    logger.error(f"Unexpected value error with ID {uid}:\n{exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": exc.details},
    )


@app.exception_handler(ex.NotEnabledError)
async def not_enabled_error_handler(request: Request, exc: ex.NotEnabledError):
    uid = uuid7()
    logger.error(f"Operation not enabled error with ID {uid}:\n{exc}")
    return JSONResponse(
        status_code=501,
        content={"detail": "operation not enabled"},
    )


@app.exception_handler(ex.UnknownError)
async def unknown_error_exception_handler(request: Request, exc: ex.UnknownError):
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
# Include routers based on environment
app.include_router(main_router)
if env.is_admin_mode():
    app.include_router(admin_router)
if env.is_dev_mode():
    app.include_router(dev_router)
