
import rich.traceback

from engrate_sdk.utils import log
from typing import List

from src import env

logger = log.get_logger(__name__)


def init() -> int | None:
    """Initializes the application."""
    if not env.validate():
        logger.error("Environment variables are not set correctly – aborting.")
        return 1
    init_db()
    rich.traceback.install(show_locals=True)
    log.init(env.get_log_level())
    return None

async def set_feature_flag(
    flag_data: env.FeatureFlagSpec, sessionmaker
) -> None:
    """Sets a single feature flag with the provided value."""
    flag_spec = env.FeatureFlagSpec(**flag_data)
    #TODO implement this when we decide how to handle user management
    logger.info(f"Set feature flag {flag_spec.name} to {flag_spec.value} for "
                    f"org {flag_spec.org}")

async def set_feature_flags(
    flags_data: List[env.FeatureFlagSpec], sessionmaker
) -> None:
    """Set multiple feature flags."""
    for flag_data in flags_data:
        await set_feature_flag(flag_data, sessionmaker)

def init_db():
    """Initializes the application."""
    rich.traceback.install(show_locals=True)
    log.init(env.get_log_level())

