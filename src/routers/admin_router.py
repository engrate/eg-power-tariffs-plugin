from engrate_sdk.utils import log
from fastapi import APIRouter, HTTPException

import env

logger = log.get_logger(__name__)
router = APIRouter(
    tags=["Power Tariffs API"],
    prefix="/admin",
    include_in_schema=env.is_admin_mode()
)

@router.get("/health",
            response_model=dict,
            summary="Health check endpoint")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/version",
            response_model=dict,
            summary="Version endpoint")
async def version_check():
    """Version endpoint that reads version from pyproject.toml."""
    import importlib.metadata

    def get_version():
        """Get version from installed package metadata."""
        try:
            return importlib.metadata.version('src')
        except importlib.metadata.PackageNotFoundError:
            return "unknown"

    version = get_version()

    if version == "unknown":
        raise HTTPException(
            status_code=409,
            detail="Could not determine version"
        )

    return {"version": version}


@router.get("/metrics",
            response_model=dict,
            summary="Metrics endpoint")
async def metrics_check():
    """Metrics endpoint."""
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi import Response

        metrics_data = generate_latest()
        return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Prometheus client not installed"
        )



