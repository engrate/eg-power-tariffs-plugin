import sys
import traceback
import types as pytypes
from pathlib import Path
from typing import Type

from alembic import command
from alembic.config import Config
from engrate_sdk.http.server import HttpServer
from engrate_sdk.utils import log
from engrate_sdk.utils.uuid import uuid7

from src import init,env

logger = log.get_logger(__name__)


def custom_excepthook(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: pytypes.TracebackType,
):
    """Custom exception handler that writes uncaught exceptions to a log file
    and prints a friendly message to the console."""
    # Prevent handling KeyboardInterrupt so a user can still abort the program with Ctrl+C
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    uid = uuid7()
    logger.error(f"Uncaught exception, incident ID: {uid}")

    # log exception to stderr
    traceback.print_exception(exc_type, exc_value, exc_traceback)

    try:
        logger.error(uid, exc_value, "Category: system level uncaught exception")
    except Exception:
        logger.error(f"Uncaught exception while logging incident. {exc_value}")


# Assign the custom exception handler
sys.excepthook = custom_excepthook


def run(args):
    """Runs the server."""
    logger.info("Validating environment variables with following values:")
    env.dump()
    run_status = init.init()
    if run_status:
        return run_status

    conf = env.get_http_conf()

    ## Run migrations if auto-migrate is enabled
    if env.get_auto_migrate():
        logger.info("Running migrations...")
        if Path("alembic.ini").exists():
            alembic_cfg = Config("alembic.ini")
        elif (path := Path.cwd().parent / "alembic.ini") and path.exists():
            alembic_cfg = Config(path)
        else:
            logger.error(
                "No alembic.ini file found. Please ensure it exists in the current workspace."
            )
            return 3

        alembic_cfg.set_main_option("script_location", "src:migrations")
        command.upgrade(alembic_cfg, "head")

    if conf.debug and conf.autoreload:
        import jurigged
        from jurigged.live import conservative_logger

        jurigged.watch("/", logger=conservative_logger)

    HttpServer.run(conf, "api:app")
    logger.info("Server stopped.")
    return 0


def main():
    """Main entry point."""
    sys.exit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
