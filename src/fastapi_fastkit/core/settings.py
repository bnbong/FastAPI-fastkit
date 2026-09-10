# --------------------------------------------------------------------------
# The Module defines fastapi-fastkit project's general Env settings.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from enum import StrEnum
from pathlib import Path

from .exceptions import BackendExceptions


class FeatureAxis(StrEnum):
    """Canonical keys of every axis in :attr:`FastkitConfig.PACKAGE_CATALOG`.

    The interactive config dict is keyed by these strings, and both
    ``DynamicConfigGenerator`` and ``DependencyCollector`` look choices up
    through them. Keeping the literals in one place stops the three modules
    from drifting apart (a typo used to mean "selected but never generated").
    """

    DATABASE = "database"
    AUTHENTICATION = "authentication"
    ASYNC_TASKS = "async_tasks"
    TESTING = "testing"
    CACHING = "caching"
    MONITORING = "monitoring"
    UTILITIES = "utilities"
    MIGRATIONS = "migrations"
    TOOLING = "tooling"
    LOGGING = "logging"


#: Sentinel choice meaning "user opted out of this axis".
NONE_CHOICE = "None"

#: Axes whose selection is a list of choices rather than a single choice.
MULTI_SELECT_AXES: tuple[str, ...] = (
    FeatureAxis.UTILITIES,
    FeatureAxis.TOOLING,
)


class DatabaseChoice(StrEnum):
    """Options of the ``database`` axis."""

    POSTGRESQL = "PostgreSQL"
    MYSQL = "MySQL"
    MONGODB = "MongoDB"
    REDIS = "Redis"
    SQLITE = "SQLite"
    NONE = NONE_CHOICE


class AuthChoice(StrEnum):
    """Options of the ``authentication`` axis."""

    JWT = "JWT"
    OAUTH2 = "OAuth2"
    FASTAPI_USERS = "FastAPI-Users"
    SESSION = "Session-based"
    NONE = NONE_CHOICE


class AsyncTaskChoice(StrEnum):
    """Options of the ``async_tasks`` axis."""

    CELERY = "Celery"
    DRAMATIQ = "Dramatiq"
    NONE = NONE_CHOICE


class TestingChoice(StrEnum):
    """Options of the ``testing`` axis."""

    BASIC = "Basic"
    COVERAGE = "Coverage"
    ADVANCED = "Advanced"
    NONE = NONE_CHOICE


class CachingChoice(StrEnum):
    """Options of the ``caching`` axis."""

    REDIS = "Redis"
    NONE = NONE_CHOICE


class MonitoringChoice(StrEnum):
    """Options of the ``monitoring`` axis."""

    LOGURU = "Loguru"
    OPENTELEMETRY = "OpenTelemetry"
    PROMETHEUS = "Prometheus"
    NONE = NONE_CHOICE


class UtilityChoice(StrEnum):
    """Options of the ``utilities`` axis (multi-select)."""

    CORS = "CORS"
    RATE_LIMITING = "Rate-Limiting"
    PAGINATION = "Pagination"
    WEBSOCKET = "WebSocket"
    NONE = NONE_CHOICE


class MigrationsChoice(StrEnum):
    """Options of the ``migrations`` axis."""

    ALEMBIC = "Alembic"
    NONE = NONE_CHOICE


class ToolingChoice(StrEnum):
    """Options of the ``tooling`` axis (multi-select)."""

    RUFF = "ruff"
    PRE_COMMIT = "pre-commit"
    GITHUB_ACTIONS = "github-actions"
    DEVCONTAINER = "devcontainer"
    MAKEFILE = "makefile"
    NONE = NONE_CHOICE


class LoggingChoice(StrEnum):
    """Options of the ``logging`` axis."""

    STRUCTURED = "structured"
    NONE = NONE_CHOICE


class FastkitConfig:
    # Overridable values
    FASTKIT_PROJECT_ROOT: str = ""  # default : None (will be overridden)
    FASTKIT_TEMPLATE_ROOT: str = ""  # default : None (will be overridden)
    LOG_FILE_PATH: str = ""  # default : None (will be overridden)
    USER_WORKSPACE: str = ""  # default : None (will be overridden)

    # Default Options
    DEBUG_MODE: bool = False
    LOGGING_LEVEL: str = "DEBUG"

    # Template Metadata Options
    TEMPLATE_PATHS: dict[str, list[str] | dict[str, list[str]]] = {
        "main": [
            "src/main.py",
            "src/app/main.py",
            "main.py",
        ],
        "setup": [
            "setup.py",
            "src/setup.py",
        ],
        "pyproject": [
            "pyproject.toml",
        ],
        "config": {
            "files": ["settings.py", "config.py"],
            "paths": [
                "src/core",
                "src/app/core",
                "src",
                "",
            ],
        },
    }

    # Architecture Presets (interactive ``init`` wizard)
    #
    # The preset shapes how the generated project is laid out (single file vs.
    # layered vs. domain-oriented). Preset-specific generation logic lives in
    # later issues — this catalog is the user-facing menu and the canonical
    # set of preset ids persisted in the interactive config.
    ARCHITECTURE_PRESETS: dict[str, str] = {
        "minimal": "Smallest viable FastAPI app — a single app + a couple of files.",
        "single-module": "Everything in one module; ideal for tiny scripts and prototypes.",
        "classic-layered": "Layered split: api/routes, crud, schemas, core (a la fastapi-default).",
        "domain-starter": "Domain-oriented: src/app/domains/<concept>/ with router/service/repository (recommended).",
    }
    DEFAULT_ARCHITECTURE_PRESET: str = "domain-starter"

    # Startproject Options
    PROJECT_STACKS: dict[str, list[str]] = {
        "minimal": ["fastapi", "uvicorn", "pydantic", "pydantic-settings"],
        "standard": [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "alembic",
            "pytest",
            "pydantic",
            "pydantic-settings",
        ],
        "full": [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "alembic",
            "pytest",
            "redis",
            "celery",
            "pydantic",
            "pydantic-settings",
        ],
    }

    # Package Manager Options
    #
    # Subprocess timeouts (seconds). Every package manager invocation is bound
    # by one of these so a hung child process can never block the CLI forever.
    # ``FASTKIT_SUBPROCESS_TIMEOUT`` overrides all of them at runtime.
    SUBPROCESS_TIMEOUT_ENV_VAR: str = "FASTKIT_SUBPROCESS_TIMEOUT"
    SUBPROCESS_TIMEOUTS: dict[str, int] = {
        "check": 30,
        "venv": 120,
        "install": 900,
        "default": 300,
    }

    DEFAULT_PACKAGE_MANAGER: str = "uv"
    SUPPORTED_PACKAGE_MANAGERS: list[str] = ["pip", "uv", "pdm", "poetry"]
    PACKAGE_MANAGER_CONFIG: dict[str, dict[str, str]] = {
        "pip": {
            "dependency_file": "requirements.txt",
            "executable": "pip",
            "description": "Standard Python package manager",
        },
        "uv": {
            "dependency_file": "pyproject.toml",
            "executable": "uv",
            "description": "Fast Python package manager",
        },
        "pdm": {
            "dependency_file": "pyproject.toml",
            "executable": "pdm",
            "description": "Modern Python dependency management",
        },
        "poetry": {
            "dependency_file": "pyproject.toml",
            "executable": "poetry",
            "description": "Python dependency management and packaging",
        },
    }

    # Package Catalog for Interactive Mode (v1.2.0+)
    # Based on recommendations from: https://github.com/mjhea0/awesome-fastapi
    PACKAGE_CATALOG: dict[str, dict[str, list[str]]] = {
        FeatureAxis.DATABASE: {
            DatabaseChoice.POSTGRESQL: ["asyncpg", "sqlalchemy"],
            DatabaseChoice.MYSQL: ["aiomysql", "sqlalchemy"],
            DatabaseChoice.MONGODB: ["motor"],
            # ``aioredis`` is abandoned (merged into redis-py) and does not
            # install on Python 3.12 — redis[hiredis] ships the asyncio client.
            DatabaseChoice.REDIS: ["redis[hiredis]"],
            DatabaseChoice.SQLITE: ["sqlalchemy", "aiosqlite"],
            DatabaseChoice.NONE: [],
        },
        FeatureAxis.AUTHENTICATION: {
            AuthChoice.JWT: ["pyjwt[crypto]", "pwdlib[argon2]"],
            # SessionMiddleware (used by the OAuth2 login flow) needs itsdangerous.
            AuthChoice.OAUTH2: ["authlib", "itsdangerous", "httpx"],
            AuthChoice.FASTAPI_USERS: [
                "fastapi-users[sqlalchemy]",
                "pyjwt[crypto]",
                "pwdlib[argon2]",
            ],
            AuthChoice.SESSION: ["itsdangerous"],
            AuthChoice.NONE: [],
        },
        FeatureAxis.ASYNC_TASKS: {
            AsyncTaskChoice.CELERY: ["celery[redis]", "redis[hiredis]"],
            AsyncTaskChoice.DRAMATIQ: ["dramatiq[redis]", "redis[hiredis]"],
            AsyncTaskChoice.NONE: [],
        },
        FeatureAxis.TESTING: {
            TestingChoice.BASIC: ["pytest", "pytest-asyncio", "httpx"],
            TestingChoice.COVERAGE: [
                "pytest",
                "pytest-asyncio",
                "pytest-cov",
                "httpx",
            ],
            TestingChoice.ADVANCED: [
                "pytest",
                "pytest-asyncio",
                "pytest-cov",
                "httpx",
                "faker",
                "factory-boy",
            ],
            TestingChoice.NONE: [],
        },
        FeatureAxis.CACHING: {
            # fastapi-cache2 imports starlette.templating at module scope,
            # which hard-requires jinja2 — without it the app fails to import.
            CachingChoice.REDIS: ["redis[hiredis]", "fastapi-cache2", "jinja2"],
            CachingChoice.NONE: [],
        },
        FeatureAxis.MONITORING: {
            MonitoringChoice.LOGURU: ["loguru"],
            MonitoringChoice.OPENTELEMETRY: [
                "opentelemetry-api",
                "opentelemetry-sdk",
                "opentelemetry-instrumentation-fastapi",
                "opentelemetry-exporter-otlp-proto-http",
            ],
            MonitoringChoice.PROMETHEUS: [
                "prometheus-client",
                "prometheus-fastapi-instrumentator",
            ],
            MonitoringChoice.NONE: [],
        },
        FeatureAxis.UTILITIES: {
            UtilityChoice.CORS: [],  # Built-in to FastAPI
            UtilityChoice.RATE_LIMITING: ["slowapi"],
            UtilityChoice.PAGINATION: ["fastapi-pagination"],
            UtilityChoice.WEBSOCKET: ["websockets"],
            UtilityChoice.NONE: [],
        },
        FeatureAxis.MIGRATIONS: {
            MigrationsChoice.ALEMBIC: ["alembic"],
            MigrationsChoice.NONE: [],
        },
        FeatureAxis.TOOLING: {
            ToolingChoice.RUFF: ["ruff"],
            ToolingChoice.PRE_COMMIT: ["pre-commit"],
            ToolingChoice.GITHUB_ACTIONS: [],  # workflow file only
            ToolingChoice.DEVCONTAINER: [],  # devcontainer.json only
            ToolingChoice.MAKEFILE: [],  # Makefile only
            ToolingChoice.NONE: [],
        },
        FeatureAxis.LOGGING: {
            # Stdlib ``logging`` + ``json`` only — no third-party dependency.
            LoggingChoice.STRUCTURED: [],
            LoggingChoice.NONE: [],
        },
    }

    # Feature descriptions for display in interactive mode
    FEATURE_DESCRIPTIONS: dict[str, str] = {
        FeatureAxis.DATABASE: "Database and ORM selection",
        FeatureAxis.AUTHENTICATION: "User authentication and authorization",
        FeatureAxis.ASYNC_TASKS: "Background task processing",
        FeatureAxis.TESTING: "Testing framework and tools",
        FeatureAxis.CACHING: "Response and data caching",
        FeatureAxis.MONITORING: "Application monitoring and logging",
        FeatureAxis.UTILITIES: "Additional utilities and middleware",
        FeatureAxis.MIGRATIONS: "Database schema migrations",
        FeatureAxis.TOOLING: "Developer tooling and CI configuration",
        FeatureAxis.LOGGING: "Application logging format",
    }

    # Testing Options
    TEST_SERVER_PORT: int = 8000
    TEST_DEFAULT_TERMINAL_WIDTH: int = 80
    TEST_MAX_TERMINAL_WIDTH: int = 1000

    @classmethod
    def get_subprocess_timeout(cls, kind: str = "default") -> int:
        """
        Resolve the subprocess timeout (in seconds) for a kind of operation.

        The ``FASTKIT_SUBPROCESS_TIMEOUT`` environment variable overrides every
        built-in value; an invalid value is ignored in favour of the default.

        :param kind: One of ``check``, ``venv``, ``install`` or ``default``
        :return: Timeout in seconds
        """
        override = os.environ.get(cls.SUBPROCESS_TIMEOUT_ENV_VAR)
        if override:
            try:
                parsed = int(override)
            except ValueError:
                parsed = 0
            if parsed > 0:
                return parsed

        return cls.SUBPROCESS_TIMEOUTS.get(kind, cls.SUBPROCESS_TIMEOUTS["default"])

    def set_debug_mode(self, debug_mode: bool = True) -> None:
        self.DEBUG_MODE = debug_mode

    @staticmethod
    def __get_fastapi_fastkit_root() -> Path:
        """
        Returns the root directory of the installed FastAPI-fastkit package.
        For development: returns the project root
        For installed package: returns the package installation directory
        """
        try:
            import fastapi_fastkit

            package_root = Path(fastapi_fastkit.__file__).parent.parent
            if package_root.name == "site-packages":
                return package_root / "fastapi_fastkit"
            return package_root
        except ImportError:
            # Fallback for development environment
            return Path(__file__).parent.parent.parent.parent

    @staticmethod
    def __get_template_root() -> Path:
        """
        Returns the template directory of the installed FastAPI-fastkit package.
        For development: returns the project template directory
        For installed package: returns the package template directory
        """
        try:
            import fastapi_fastkit

            package_root = Path(fastapi_fastkit.__file__).parent
            template_dir = package_root / "fastapi_project_template"
            if template_dir.exists():
                return template_dir
            # If inside site-packages
            if package_root.parent.name == "site-packages":
                return (
                    package_root.parent / "fastapi_fastkit" / "fastapi_project_template"
                )
            return package_root.parent / "fastapi_project_template"
        except ImportError:
            # Fallback for development environment
            return Path(__file__).parent.parent / "fastapi_project_template"

    @classmethod
    def __init__(cls) -> None:
        """
        Initialize the configuration by performing important checks and setups.
        Override directories to correct position.
        """
        cls.FASTKIT_PROJECT_ROOT = str(cls.__get_fastapi_fastkit_root())
        cls.FASTKIT_TEMPLATE_ROOT = str(cls.__get_template_root())
        cls.LOG_FILE_PATH = os.path.join(
            cls.FASTKIT_PROJECT_ROOT, "logs", "fastkit.log"
        )
        cls.USER_WORKSPACE = os.getcwd()

        # Validate the configurations
        cls._validate()

    @classmethod
    def _validate(cls) -> None:
        """
        Validate the configuration settings to ensure that they are correct.
        Raises an error if validation fails.
        """
        if not cls.FASTKIT_PROJECT_ROOT or not os.path.isdir(cls.FASTKIT_PROJECT_ROOT):
            raise BackendExceptions(
                "FASTKIT_PROJECT_ROOT is not allocated to valid directory."
            )

        if not cls.FASTKIT_TEMPLATE_ROOT or not os.path.isdir(cls.FASTKIT_PROJECT_ROOT):
            raise BackendExceptions(
                "FASTKIT_TEMPLATE_ROOT is not allocated to valid directory."
            )

        log_dir = os.path.dirname(cls.LOG_FILE_PATH)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)


settings = FastkitConfig()
