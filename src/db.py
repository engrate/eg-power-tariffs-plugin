import asyncio
import functools
import inspect
import ssl
from datetime import datetime, timedelta
from typing import Optional, Any

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from engrate_sdk.utils import log
from src import env
from src import app

logger = log.get_logger(__name__)


class ConnectionState(BaseModel):
    """Type for connection state."""

    engine: Any  # AsyncEngine
    sessionmaker: Any  # SessionMaker


async def start() -> ConnectionState:
    url = env.get_postgres_url()
    if cafile := env.get_postgres_conf().tls_ca_pem_path:
        engine = create_async_engine(
            url, connect_args={"ssl": ssl.create_default_context(cafile=cafile)}
        )
    else:
        engine = create_async_engine(url)
    # NOTE: set `echo=True` to log a SQL trace
    maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    return ConnectionState(engine=engine, sessionmaker=maker)


async def stop(state: ConnectionState):
    """Stop the engine."""
    await state.engine.dispose()


async def await_up(state: ConnectionState, timeout: Optional[float] = None) -> None:
    """Wait for the engine to be up."""
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=timeout) if timeout else None
    while (not end_time) or (datetime.now() < end_time):
        try:
            await _check_connection(state)
            return
        except Exception as e:
            logger.warning(
                f"Can't connect to Postgres - retrying: {type(e).__name__}: {e}"
            )
            await asyncio.sleep(1)


async def _check_connection(state: ConnectionState) -> None:
    """Check the connection to the database."""
    async with state.sessionmaker() as session:
        async with session.begin():
            await session.execute(text("SELECT 1"))


def with_session(func):
    """
    Decorator to inject a database session into a function.

    This decorator automatically provides an AsyncSession to the decorated function.
    It will be passed as the 'session' parameter, or if 'session' is already provided
    by the caller, it will use that instead.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if "session" in kwargs and kwargs["session"] is not None:
            return await func(*args, **kwargs)

        # Check if the function expects a session parameter
        sig = inspect.signature(func)
        if "session" not in sig.parameters:
            raise ValueError(
                f"Function {func.__name__} must have a 'session' parameter"
            )

        # Get a new session
        async with app.state.db.sessionmaker() as session:
            try:
                kwargs["session"] = session
                result = await func(*args, **kwargs)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise

    return wrapper
