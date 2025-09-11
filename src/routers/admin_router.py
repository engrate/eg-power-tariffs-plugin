from engrate_sdk.utils import log
from fastapi import APIRouter, HTTPException

from src import env

logger = log.get_logger(__name__)
router = APIRouter(
    tags=["Power Tariffs API"], prefix="/admin", include_in_schema=env.is_admin_mode()
)


@router.get("/health", response_model=dict, summary="Health check endpoint")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/version", response_model=dict, summary="Version endpoint")
async def version_check():
    """Version endpoint that reads version from pyproject.toml."""
    import importlib.metadata

    def get_version():
        """Get version from installed package metadata."""
        try:
            return importlib.metadata.version("src")
        except importlib.metadata.PackageNotFoundError:
            return "unknown"

    version = get_version()

    if version == "unknown":
        raise HTTPException(status_code=409, detail="Could not determine version")

    return {"version": version}
