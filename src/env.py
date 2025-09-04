import json
from typing import cast

from engrate_sdk.http import server as http_server
from engrate_sdk.utils import env, log
from pydantic import BaseModel
from pydantic.networks import HttpUrl

logger = log.get_logger(__name__)

#### Provision Types ####


class FeatureFlagSpec(BaseModel):
    org: str
    name: str
    value: bool


#### Types ####


class PostgresConnectionConf(BaseModel):
    database: str
    host: str
    username: str
    password: str
    port: int
    use_tls: bool = False
    tls_ca_pem_path: str | None = None


#### Env Vars ####

## Alerting ##

SLACK_WEBHOOK_URL = env.EnvVarSpec(
    id="SLACK_WEBHOOK_URL", type=(HttpUrl, ...), is_secret=True
)


CORS_ALLOW_ORIGINS = env.EnvVarSpec(
    id="CORS_ALLOW_ORIGINS",
    type=(list[str], ...),
    parse=lambda x: x.split(","),
    default="",
)

## HTTP ##

HTTP_HOST = env.EnvVarSpec(id="HTTP_HOST", default="0.0.0.0")

HTTP_PORT = env.EnvVarSpec(id="HTTP_PORT", default="3011")

HTTP_DEBUG = env.EnvVarSpec(
    id="HTTP_DEBUG",
    parse=lambda x: x.lower() == "true",
    default="false",
    type=(bool, ...),
)

HTTP_AUTORELOAD = env.EnvVarSpec(
    id="HTTP_AUTORELOAD",
    parse=lambda x: x.lower() == "true",
    default="false",
    type=(bool, ...),
)

## Logging ##

LOG_LEVEL = env.EnvVarSpec(id="LOG_LEVEL", default="INFO")

## Migrations ##

AUTO_MIGRATE = env.EnvVarSpec(
    id="AUTO_MIGRATE",
    parse=lambda x: x.lower() == "true",
    default="false",
    type=(bool, ...),
)


## Provisioning ##

SET_FEATURE_FLAGS = env.EnvVarSpec(
    id="SET_FEATURE_FLAGS",
    parse=lambda x: json.loads(x) if x else None,
    default="",
    type=(list[FeatureFlagSpec] | None, ...),
)


LOAD_TARIFFS_DEFINITIONS = env.EnvVarSpec(
    id="LOAD_TARIFFS_DEFINITIONS",
    parse=lambda x: x.lower() == "true",
    default="false",
    type=(bool, ...),
)

LOAD_OPERATORS = env.EnvVarSpec(
    id="LOAD_OPERATORS",
    parse=lambda x: x.lower() == "true",
    default="false",
    type=(bool, ...),
)

LOAD_METERING_GRID_AREAS = env.EnvVarSpec(
    id="LOAD_METERING_GRID_AREAS",
    parse=lambda x: x.lower() == "true",
    default="false",
    type=(bool, ...),
)

DEV_MODE = env.EnvVarSpec(
    id="DEV_MODE",
    parse=lambda x: x.lower() == "true",
    default="false",
    type=(bool, ...),
)

ADMIN_MODE = env.EnvVarSpec(
    id="ADMIN_MODE",
    parse=lambda x: x.lower() == "true",
    default="false",
    type=(bool, ...),
)
## Postgres ##

POSTGRES_DATABASE = env.EnvVarSpec(id="POSTGRES_DATABASE")
POSTGRES_USERNAME = env.EnvVarSpec(id="POSTGRES_USERNAME")
POSTGRES_PASSWORD = env.EnvVarSpec(id="POSTGRES_PASSWORD", is_secret=True)
POSTGRES_HOST = env.EnvVarSpec(id="POSTGRES_HOST")
POSTGRES_PORT = env.EnvVarSpec(id="POSTGRES_PORT", default="5432")

POSTGRES_USE_TLS = env.EnvVarSpec(
    id="POSTGRES_USE_TLS",
    default="false",
    parse=lambda x: x.lower() == "true",
    type=(bool, ...),
)
POSTGRES_TLS_CA_PEM_PATH = env.EnvVarSpec(
    id="POSTGRES_TLS_CA_PEM_PATH",
    default="",
    parse=lambda x: x or None,
    type=(str | None, ...),
)

##SDK
REGISTRAR_URL = env.EnvVarSpec(
    id="REGISTRAR_URL",
    type=(str, ...),
)

AUTO_REGISTER = env.EnvVarSpec(
    id="AUTO_REGISTER",
    default="true",
    parse=lambda x: x.lower() == "true",
    type=(bool, ...),
)

## Elområden##
ELOMRADEN_BASE_URL = env.EnvVarSpec(id="ELOMRADEN_BASE_URL", type=(str, ...))
ELOMRADEN_APIKEY = env.EnvVarSpec(
    id="ELOMRADEN_APIKEY", type=(str, ...), is_secret=True
)

ELOMRADEN_USER = env.EnvVarSpec(id="ELOMRADEN_USER", type=(str, ...), is_secret=True)

#### API ####


def validate() -> bool:
    return env.validate(
        [
            HTTP_PORT,
            HTTP_DEBUG,
            HTTP_AUTORELOAD,
            LOG_LEVEL,
            ELOMRADEN_APIKEY,
            ELOMRADEN_USER,
            ELOMRADEN_BASE_URL,
            AUTO_MIGRATE,
            SET_FEATURE_FLAGS,
            POSTGRES_USERNAME,
            POSTGRES_PASSWORD,
            POSTGRES_HOST,
            POSTGRES_DATABASE,
            POSTGRES_PORT,
            POSTGRES_TLS_CA_PEM_PATH,
            REGISTRAR_URL,
        ]
    )

def dump():
    """Dumps the environment variables to a JSON string."""
    env_vars = {
        "CORS_ALLOW_ORIGINS": get_cors_allowed_origins(),
        "HTTP_HOST": get_http_conf().host,
        "HTTP_PORT": get_http_conf().port,
        "HTTP_DEBUG": get_http_conf().debug,
        "HTTP_AUTORELOAD": get_http_conf().autoreload,
        "LOG_LEVEL": get_log_level(),
        "SET_FEATURE_FLAGS": get_set_feature_flags(),
        "AUTO_MIGRATE": get_auto_migrate(),
        "ELOMRADEN_APIKEY": get_elomraden_apikey(),
        "ELOMRADEN_USER": get_elomraden_user(),
        "ELOMRADEN_BASE_URL": get_elomraden_base_url(),
        "POSTGRES_CONF": get_postgres_conf().model_dump(),
        "REGISTRAR_URL": get_registrar_url(),
        "AUTO_REGISTER": get_auto_register(),
    }
    print(env_vars)

def get_slack_webhook_url() -> str:
    return cast(str, env.parse(SLACK_WEBHOOK_URL))


def get_oauth2_client_id() -> str:
    return "power-tariffs-pg"  # env.parse(AUTH_OAUTH2_CLIENT_ID)


def get_cors_allowed_origins() -> list[str]:
    return cast(list[str], env.parse(CORS_ALLOW_ORIGINS))


def get_http_conf() -> http_server.ServerConf:
    return http_server.ServerConf(
        host=cast(str, env.parse(HTTP_HOST)),
        port=cast(int, env.parse(HTTP_PORT)),
        debug=cast(bool, env.parse(HTTP_DEBUG)),
        autoreload=cast(bool, env.parse(HTTP_AUTORELOAD)),
    )


def get_log_level() -> str:
    return cast(str, env.parse(LOG_LEVEL))


def get_set_feature_flags():
    return cast(list[FeatureFlagSpec], env.parse(SET_FEATURE_FLAGS))


def get_auto_migrate() -> bool:
    return cast(bool, env.parse(AUTO_MIGRATE))


def get_elomraden_apikey() -> str:
    return cast(str, env.parse(ELOMRADEN_APIKEY))


def get_elomraden_user() -> str:
    return cast(str, env.parse(ELOMRADEN_USER))


def get_elomraden_base_url() -> str:
    return cast(str, env.parse(ELOMRADEN_BASE_URL))


def get_postgres_conf() -> PostgresConnectionConf:
    return PostgresConnectionConf(
        host=cast(str, env.parse(POSTGRES_HOST)),
        database=cast(str, env.parse(POSTGRES_DATABASE)),
        username=cast(str, env.parse(POSTGRES_USERNAME)),
        password=cast(str, env.parse(POSTGRES_PASSWORD)),
        port=cast(int, env.parse(POSTGRES_PORT)),
        use_tls=cast(bool, env.parse(POSTGRES_USE_TLS)),
        tls_ca_pem_path=env.parse(POSTGRES_TLS_CA_PEM_PATH),
    )


def get_postgres_url():
    conf = get_postgres_conf()
    scheme = "postgresql+asyncpg"
    user = conf.username
    db = conf.database
    url = f"{scheme}://{user}:{conf.password}@{conf.host}:{conf.port}/{db}"
    if conf.use_tls:
        url += "?sslmode=require"
    return url


def get_registrar_url():
    return env.parse(REGISTRAR_URL)


def get_auto_register() -> bool:
    return cast(bool, env.parse(AUTO_REGISTER))

def must_load_tariffs_definitions() -> bool:
    return cast(bool, env.parse(LOAD_TARIFFS_DEFINITIONS))

def must_load_operators() -> bool:
    return cast(bool, env.parse(LOAD_OPERATORS))

def must_load_metering_grid_areas() -> bool:
    return cast(bool, env.parse(LOAD_METERING_GRID_AREAS))

def is_dev_mode()-> bool:
    return cast(bool, env.parse(DEV_MODE))

def is_admin_mode()-> bool:
    return cast(bool, env.parse(ADMIN_MODE))
