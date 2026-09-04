# --------------------------------------------------------------------------
# Dynamic configuration file generation based on user selections
#
# Turns one interactive-``init`` configuration mapping into the complete set
# of files a project needs for the features the user picked: ``main.py``,
# database / auth modules, background workers and their routes, cache,
# WebSocket and pagination routers, structured logging, Alembic migrations,
# developer tooling and the Docker files.
#
# Every artifact is rendered from a Jinja2 fragment stored in
# ``src/fastapi_fastkit/fragments``. See ``fragments/README.md`` for the
# directory layout and the recipe for adding a new feature.
#
# ``generate_all_files()`` is the single entry point: it resolves every
# artifact for the configuration and writes it to disk. ``planned_files()``
# answers the same question without writing anything (``--dry-run``).
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import hashlib
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from jinja2 import Environment, PackageLoader

from fastapi_fastkit.core.settings import (
    NONE_CHOICE,
    AsyncTaskChoice,
    AuthChoice,
    CachingChoice,
    DatabaseChoice,
    FeatureAxis,
    LoggingChoice,
    MigrationsChoice,
    MonitoringChoice,
    TestingChoice,
    ToolingChoice,
    UtilityChoice,
)

#: Dotted SQLAlchemy URLs per relational database choice.
SQLALCHEMY_URLS: Dict[str, str] = {
    DatabaseChoice.POSTGRESQL: "postgresql+asyncpg://user:password@localhost/dbname",
    DatabaseChoice.MYSQL: "mysql+aiomysql://user:password@localhost/dbname",
    DatabaseChoice.SQLITE: "sqlite+aiosqlite:///./app.db",
}

#: Databases handled by the SQLAlchemy fragment (and by Alembic).
SQL_DATABASES: Tuple[str, ...] = tuple(SQLALCHEMY_URLS)

#: docker-compose service name per database choice.
COMPOSE_DB_SERVICES: Dict[str, str] = {
    DatabaseChoice.POSTGRESQL: "postgres",
    DatabaseChoice.MYSQL: "mysql",
    DatabaseChoice.MONGODB: "mongodb",
    DatabaseChoice.REDIS: "redis",
}

#: docker-compose named volume per database service.
_COMPOSE_DB_VOLUMES: Dict[str, str] = {
    "postgres": "postgres_data",
    "mysql": "mysql_data",
    "mongodb": "mongo_data",
}

#: Default entrypoint when the caller does not describe the project layout.
DEFAULT_MAIN_RELPATH = "src/main.py"
DEFAULT_DB_CONFIG_RELPATH = "src/config/database.py"
DEFAULT_AUTH_CONFIG_RELPATH = "src/config/auth.py"

#: Files written with the executable bit set.
_EXECUTABLE_ARTIFACTS = frozenset({"scripts/migrate.sh"})


@lru_cache(maxsize=1)
def get_environment() -> Environment:
    """
    Build (once) the Jinja2 environment backed by the ``fragments`` package.

    Returns:
        Configured Jinja2 environment
    """
    return Environment(
        loader=PackageLoader("fastapi_fastkit", "fragments"),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )


def _dotted(relpath: str) -> str:
    """Convert a project-relative module path into its dotted import path."""
    normalized = relpath.replace("\\", "/").strip("/")
    if normalized.endswith(".py"):
        normalized = normalized[: -len(".py")]
    return normalized.replace("/", ".")


def _import_group(line: str, first_party_root: str) -> int:
    """Bucket an import line the way isort's ``profile=black`` would.

    ``0`` standard library, ``1`` third party, ``2`` first party. Used to
    emit an already-sorted import block so the generated ``main.py`` passes
    ``isort``/``ruff check`` straight out of the generator.
    """
    stripped = line.strip()
    if stripped.startswith("from "):
        module = stripped.split(" ", 2)[1]
    elif stripped.startswith("import "):
        module = stripped.split(" ", 1)[1].split(" as ")[0]
    else:  # comment lines ride along with the third-party block
        return 1

    root = module.split(".", 1)[0]
    if root == first_party_root:
        return 2
    if root in sys.stdlib_module_names:
        return 0
    return 1


def _slugify(name: str) -> str:
    """Reduce a project name to a lowercase, hyphenated identifier."""
    slug = "".join(char if char.isalnum() else "-" for char in name.lower())
    slug = "-".join(part for part in slug.split("-") if part)
    return slug or "app"


@dataclass
class MainSections:
    """The fragments composing one generated ``main.py``."""

    #: Fragments contributing import statements (sorted before rendering).
    import_fragments: list[str] = field(default_factory=list)
    #: 4-space-indented statements inside the lifespan handler.
    lifespan_fragments: list[str] = field(default_factory=list)
    #: Top-level statements placed right after ``app = FastAPI(...)``.
    setup_fragments: list[str] = field(default_factory=list)
    #: Whether any fragment reads ``os.environ``, so ``main.py`` imports ``os``.
    needs_os: bool = False


class DynamicConfigGenerator:
    """
    Generates configuration files based on project config.

    This class turns the interactive selections into concrete files. It knows
    *what* to generate and *where* (project-relative) each artifact belongs;
    the caller supplies the layout paths so the same generator serves every
    architecture preset.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        project_dir: str,
        *,
        app_module: str = "src.main:app",
        main_py_relpath: str = DEFAULT_MAIN_RELPATH,
        db_config_relpath: str = DEFAULT_DB_CONFIG_RELPATH,
        auth_config_relpath: str = DEFAULT_AUTH_CONFIG_RELPATH,
    ) -> None:
        """
        Initialize config generator.

        Args:
            config: Project configuration dictionary
            project_dir: Path to the project directory
            app_module: ``module:attr`` uvicorn entrypoint of the layout
            main_py_relpath: Project-relative path of the application entrypoint
            db_config_relpath: Project-relative path of the database module
            auth_config_relpath: Project-relative path of the auth module
        """
        self.config = config
        self.project_dir = Path(project_dir)
        self.app_module = app_module
        self.main_py_relpath = main_py_relpath
        self.db_config_relpath = db_config_relpath
        self.auth_config_relpath = auth_config_relpath

    # ----------------------------------------------------------------- #
    # Layout helpers
    # ----------------------------------------------------------------- #
    @property
    def package_dir(self) -> str:
        """Project-relative directory holding the application package."""
        parent = self.main_py_relpath.replace("\\", "/").rsplit("/", 1)[0]
        return parent if parent and parent != self.main_py_relpath else "src"

    @property
    def pkg(self) -> str:
        """Dotted import path of the application package (``src``, ``src.app``)."""
        return self.package_dir.replace("/", ".")

    @property
    def db_module(self) -> str:
        """Dotted import path of the generated database module."""
        return _dotted(self.db_config_relpath)

    @property
    def auth_module(self) -> str:
        """Dotted import path of the generated auth module."""
        return _dotted(self.auth_config_relpath)

    # ----------------------------------------------------------------- #
    # Rendering helpers
    # ----------------------------------------------------------------- #
    @staticmethod
    def _render(template_name: str, **context: Any) -> str:
        """
        Render a fragment template.

        Args:
            template_name: Path of the fragment relative to ``fragments/``
            context: Template variables

        Returns:
            Rendered content
        """
        return get_environment().get_template(template_name).render(**context)

    def _render_module(self, template_name: str, **context: Any) -> str:
        """Render a fragment with the layout context every module needs."""
        return self._render(
            template_name,
            pkg=self.pkg,
            package_dir=self.package_dir,
            db_module=self.db_module,
            auth_module=self.auth_module,
            app_module=self.app_module,
            project_name=self.config.get("project_name", "FastAPI App"),
            project_slug=_slugify(str(self.config.get("project_name", "app"))),
            **context,
        )

    @staticmethod
    def _build_header(title: str) -> list[str]:
        """
        Build a standard FastAPI-fastkit header comment.

        Args:
            title: Title of the file

        Returns:
            List of header lines
        """
        return DynamicConfigGenerator._render("header.j2", title=title).splitlines()

    @staticmethod
    def _join_lines(lines: list[str]) -> str:
        """
        Join lines with newline and ensure proper ending.

        Args:
            lines: List of code lines

        Returns:
            Joined string with newlines
        """
        return "\n".join(lines) + "\n"

    @staticmethod
    def _build_code_block(indent: str, *lines: str) -> list[str]:
        """
        Build a code block with consistent indentation.

        Args:
            indent: Indentation string (e.g., "    " for 4 spaces)
            lines: Lines of code to indent

        Returns:
            List of indented lines
        """
        return [f"{indent}{line}" if line else "" for line in lines]

    # ----------------------------------------------------------------- #
    # Config lookups
    # ----------------------------------------------------------------- #
    def _choice(self, axis: str) -> str:
        """Single-select choice for ``axis``, ``"None"`` when unset."""
        value = self.config.get(axis) or NONE_CHOICE
        return str(value)

    def _choices(self, axis: str) -> List[str]:
        """Multi-select choices for ``axis``, excluding the ``None`` sentinel."""
        raw = self.config.get(axis) or []
        if isinstance(raw, str):
            raw = [raw]
        return [str(item) for item in raw if str(item) != NONE_CHOICE]

    @property
    def _database_type(self) -> str:
        """Selected database type, ``"None"`` when unset."""
        database = self.config.get(FeatureAxis.DATABASE) or {}
        if isinstance(database, str):
            return database or NONE_CHOICE
        db_type = database.get("type", NONE_CHOICE)
        return str(db_type) if db_type else NONE_CHOICE

    @property
    def _auth_type(self) -> str:
        """Selected authentication type, ``"None"`` when unset."""
        return self._choice(FeatureAxis.AUTHENTICATION)

    @property
    def _uses_sql_database(self) -> bool:
        """Whether the selection is a relational database Alembic can migrate."""
        return self._database_type in SQL_DATABASES

    @property
    def _uses_ruff(self) -> bool:
        """Whether ruff replaces black + isort in the generated tooling."""
        return ToolingChoice.RUFF in self._choices(FeatureAxis.TOOLING)

    @property
    def _needs_redis_service(self) -> bool:
        """Whether docker-compose must ship a Redis service."""
        return (
            self._choice(FeatureAxis.CACHING) == CachingChoice.REDIS
            or self._choice(FeatureAxis.ASYNC_TASKS) != NONE_CHOICE
            or self._database_type == DatabaseChoice.REDIS
        )

    def _worker_command(self) -> Optional[List[str]]:
        """docker-compose ``command`` for the background worker, if any."""
        tasks = self._choice(FeatureAxis.ASYNC_TASKS)
        if tasks == AsyncTaskChoice.CELERY:
            return [
                "celery",
                "-A",
                f"{self.pkg}.worker.celery_app",
                "worker",
                "--loglevel=info",
            ]
        if tasks == AsyncTaskChoice.DRAMATIQ:
            return ["dramatiq", f"{self.pkg}.worker"]
        return None

    def _main_fragments(self) -> MainSections:
        """
        Resolve the fragments composing ``main.py`` for this configuration.

        Returns:
            The fragment paths for each section of the generated module
        """
        imports: List[str] = []
        lifespan: List[str] = []
        setup: List[str] = []

        db_type = self._database_type
        if db_type in SQL_DATABASES:
            imports.append("main/imports/sqlalchemy.j2")
            lifespan.append("main/lifespan/sqlalchemy.j2")
        elif db_type == DatabaseChoice.MONGODB:
            imports.append("main/imports/mongodb.j2")
            lifespan.append("main/lifespan/mongodb.j2")

        auth_type = self._auth_type
        if auth_type == AuthChoice.JWT:
            imports.append("main/imports/jwt.j2")
        elif auth_type == AuthChoice.FASTAPI_USERS:
            imports.append("main/imports/fastapi_users.j2")
        elif auth_type == AuthChoice.OAUTH2:
            imports.append("main/imports/oauth2.j2")
            setup.append("main/setup/oauth2.j2")
        elif auth_type == AuthChoice.SESSION:
            imports.append("main/imports/session_auth.j2")
            setup.append("main/setup/session_auth.j2")

        if self._choice(FeatureAxis.LOGGING) == LoggingChoice.STRUCTURED:
            imports.append("main/imports/structured_logging.j2")
            setup.append("main/setup/structured_logging.j2")

        utilities = self._choices(FeatureAxis.UTILITIES)
        if UtilityChoice.CORS in utilities:
            setup.append("main/setup/cors.j2")
        if UtilityChoice.RATE_LIMITING in utilities:
            imports.append("main/imports/rate_limiting.j2")
            setup.append("main/setup/rate_limiting.j2")
        if UtilityChoice.WEBSOCKET in utilities:
            imports.append("main/imports/websocket.j2")
            setup.append("main/setup/websocket.j2")
        if UtilityChoice.PAGINATION in utilities:
            imports.append("main/imports/pagination.j2")
            setup.append("main/setup/pagination.j2")

        if self._choice(FeatureAxis.ASYNC_TASKS) != NONE_CHOICE:
            imports.append("main/imports/async_tasks.j2")
            setup.append("main/setup/async_tasks.j2")

        if self._choice(FeatureAxis.CACHING) == CachingChoice.REDIS:
            imports.append("main/imports/caching.j2")
            lifespan.append("main/lifespan/caching.j2")
            setup.append("main/setup/caching.j2")

        monitoring_type = self._choice(FeatureAxis.MONITORING)
        if monitoring_type == MonitoringChoice.LOGURU:
            imports.append("main/imports/loguru.j2")
        elif monitoring_type == MonitoringChoice.PROMETHEUS:
            imports.append("main/imports/prometheus.j2")
            lifespan.append("main/lifespan/prometheus.j2")
        elif monitoring_type == MonitoringChoice.OPENTELEMETRY:
            imports.append("main/imports/opentelemetry.j2")
            setup.append("main/setup/opentelemetry.j2")

        # ``os`` is only imported when a fragment actually reads the
        # environment, so the generated module stays lint-clean.
        needs_os = bool(
            {"main/lifespan/caching.j2"} & set(lifespan)
            or {
                "main/setup/opentelemetry.j2",
                "main/setup/structured_logging.j2",
            }
            & set(setup)
        )

        return MainSections(
            import_fragments=imports,
            lifespan_fragments=lifespan,
            setup_fragments=setup,
            needs_os=needs_os,
        )

    def _build_import_groups(
        self, import_fragments: List[str], needs_os: bool
    ) -> List[List[str]]:
        """
        Render the import fragments into isort-ordered import blocks.

        Fragments are written independently of each other, so concatenating
        them verbatim produced a jumbled import block that ``isort`` (and the
        generated project's own ``make lint``) immediately rejected. Sorting
        here keeps every fragment free to declare exactly what it needs.

        Args:
            import_fragments: Fragment paths contributing import statements
            needs_os: Whether any other fragment reads ``os.environ``

        Returns:
            Standard-library / third-party / first-party blocks, in order
        """
        lines: List[str] = ["from collections.abc import AsyncIterator"]
        if needs_os:
            lines.append("import os")
        lines.extend(
            [
                "from contextlib import asynccontextmanager",
                "from fastapi import FastAPI",
                "from fastapi.middleware.cors import CORSMiddleware",
            ]
        )

        for fragment in import_fragments:
            rendered = self._render_module(fragment)
            lines.extend(line for line in rendered.splitlines() if line.strip())

        first_party_root = self.pkg.split(".", 1)[0]
        groups: List[List[str]] = [[], [], []]
        for line in dict.fromkeys(lines):  # dedupe, preserving first sighting
            groups[_import_group(line, first_party_root)].append(line)

        for group in groups:
            group.sort(key=lambda line: (not line.startswith("import "), line))

        return [group for group in groups if group]

    # ----------------------------------------------------------------- #
    # Public generators
    # ----------------------------------------------------------------- #
    def build_artifacts(self, include_main: bool = True) -> Dict[str, str]:
        """
        Resolve every file this configuration produces.

        Args:
            include_main: Whether the dynamic ``main.py`` overlay is part of
                the output. Presets that preserve their template-shipped
                entrypoint pass ``False``.

        Returns:
            Mapping of project-relative path to file content
        """
        artifacts: Dict[str, str] = {}

        if include_main:
            artifacts[self.main_py_relpath] = self.generate_main_py()

        db_config = self.generate_database_config()
        if db_config is not None:
            artifacts[self.db_config_relpath] = db_config

        auth_config = self.generate_auth_config()
        if auth_config is not None:
            artifacts[self.auth_config_relpath] = auth_config

        test_config = self.generate_test_config()
        if test_config is not None:
            artifacts["pytest.ini"] = test_config

        # The base template's own test_main.py asserts *its* root message and
        # health payload. Once the overlay replaces main.py those tests are
        # wrong, so the matching tests are regenerated with it.
        if include_main and self._choice(FeatureAxis.TESTING) != NONE_CHOICE:
            artifacts["tests/test_main.py"] = self._render_module(
                "test/test_main.py.j2", title="Application entry point tests"
            )

        artifacts.update(self.generate_feature_modules())
        artifacts.update(self.generate_migration_files())
        artifacts.update(self.generate_tooling_files())
        artifacts.update(self.generate_testing_files())

        return artifacts

    def planned_files(self, include_main: bool = True) -> List[str]:
        """
        List the project-relative files a run would create, writing nothing.

        Args:
            include_main: See :meth:`build_artifacts`

        Returns:
            Sorted list of project-relative paths
        """
        planned = set(self.build_artifacts(include_main=include_main))

        deployment = self.config.get("deployment") or []
        if "Docker" in deployment:
            planned.add("Dockerfile")
        if "docker-compose" in deployment:
            planned.add("docker-compose.yml")

        if self._uses_ruff:
            planned.add("pyproject.toml")

        return sorted(planned)

    def generate_all_files(self, include_main: bool = True) -> List[str]:
        """
        Generate every file this configuration implies, on disk.

        This is the entry point the scaffolder calls once the base template
        has been deployed. Parent directories are created as needed and
        shell scripts are written executable.

        Args:
            include_main: See :meth:`build_artifacts`

        Returns:
            Sorted list of project-relative paths that were written
        """
        written: List[str] = []

        for relpath, content in self.build_artifacts(include_main=include_main).items():
            target = self.project_dir / relpath
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            if relpath in _EXECUTABLE_ARTIFACTS:
                target.chmod(0o755)
            written.append(relpath)

        written.extend(self.generate_docker_files(app_module=self.app_module))

        if self._uses_ruff:
            written.append(self.apply_ruff_configuration())

        return sorted(set(written))

    def generate_main_py(self) -> str:
        """
        Generate main.py with selected features.

        Returns:
            Content of main.py as string
        """
        sections = self._main_fragments()
        import_groups = self._build_import_groups(
            sections.import_fragments, sections.needs_os
        )
        return self._render_module(
            "main.py.j2",
            title="FastAPI Application Main Entry Point",
            description=self.config.get("description", ""),
            version=self.config.get("version", "0.1.0"),
            import_groups=import_groups,
            lifespan_fragments=sections.lifespan_fragments,
            setup_fragments=sections.setup_fragments,
        )

    def generate_database_config(self) -> Optional[str]:
        """
        Generate database configuration.

        Returns:
            Content of database config file or None
        """
        db_type = self._database_type

        if db_type in SQL_DATABASES:
            return self._generate_sqlalchemy_config(db_type)
        if db_type == DatabaseChoice.MONGODB:
            return self._generate_mongodb_config()
        if db_type == DatabaseChoice.REDIS:
            return self._generate_redis_config()

        return None

    def _generate_sqlalchemy_config(self, db_type: str) -> str:
        """Generate SQLAlchemy database configuration."""
        return self._render_module(
            "db/sqlalchemy.py.j2",
            title="Database Configuration",
            db_type=db_type,
            database_url=SQLALCHEMY_URLS[db_type],
        )

    def _generate_mongodb_config(self) -> str:
        """Generate MongoDB configuration."""
        return self._render_module("db/mongodb.py.j2", title="MongoDB Configuration")

    def _generate_redis_config(self) -> str:
        """Generate the ``redis.asyncio`` client module."""
        return self._render_module("db/redis.py.j2", title="Redis Configuration")

    def generate_auth_config(self) -> Optional[str]:
        """
        Generate authentication configuration.

        Returns:
            Content of auth config file or None
        """
        auth_type = self._auth_type

        if auth_type == AuthChoice.JWT:
            return self._generate_jwt_config()
        if auth_type == AuthChoice.FASTAPI_USERS:
            return self._generate_fastapi_users_config()
        if auth_type == AuthChoice.OAUTH2:
            return self._render_module(
                "auth/oauth2.py.j2", title="OAuth2 Authentication Configuration"
            )
        if auth_type == AuthChoice.SESSION:
            return self._render_module(
                "auth/session.py.j2", title="Session Authentication Configuration"
            )

        return None

    def _generate_jwt_config(self) -> str:
        """Generate JWT authentication configuration."""
        return self._render_module(
            "auth/jwt.py.j2", title="JWT Authentication Configuration"
        )

    def _generate_fastapi_users_config(self) -> str:
        """Generate FastAPI-Users configuration."""
        return self._render_module(
            "auth/fastapi_users.py.j2",
            title="FastAPI-Users Authentication Configuration",
        )

    def generate_feature_modules(self) -> Dict[str, str]:
        """
        Generate the standalone modules the selected features import.

        These are the background worker, the task / cache / websocket /
        pagination routers ``main.py`` mounts, and the structured logging
        setup — everything that lives outside ``main.py`` but is referenced
        from it.

        Returns:
            Mapping of project-relative path to file content
        """
        modules: Dict[str, str] = {}
        feature_dir = f"{self.package_dir}/features"

        tasks_type = self._choice(FeatureAxis.ASYNC_TASKS)
        if tasks_type == AsyncTaskChoice.CELERY:
            modules[f"{self.package_dir}/worker.py"] = self._render_module(
                "tasks/celery_worker.py.j2", title="Celery Worker"
            )
            modules[f"{feature_dir}/tasks.py"] = self._render_module(
                "features/tasks_celery.py.j2", title="Background Task Routes"
            )
        elif tasks_type == AsyncTaskChoice.DRAMATIQ:
            modules[f"{self.package_dir}/worker.py"] = self._render_module(
                "tasks/dramatiq_worker.py.j2", title="Dramatiq Worker"
            )
            modules[f"{feature_dir}/tasks.py"] = self._render_module(
                "features/tasks_dramatiq.py.j2", title="Background Task Routes"
            )

        if self._choice(FeatureAxis.CACHING) == CachingChoice.REDIS:
            modules[f"{feature_dir}/cache.py"] = self._render_module(
                "features/cache.py.j2", title="Cached Endpoints"
            )

        utilities = self._choices(FeatureAxis.UTILITIES)
        if UtilityChoice.WEBSOCKET in utilities:
            modules[f"{feature_dir}/websocket.py"] = self._render_module(
                "features/websocket.py.j2", title="WebSocket Routes"
            )
        if UtilityChoice.PAGINATION in utilities:
            modules[f"{feature_dir}/pagination.py"] = self._render_module(
                "features/pagination.py.j2", title="Paginated Routes"
            )

        if modules:
            modules[f"{feature_dir}/__init__.py"] = self._join_lines(
                self._build_header("Generated feature routers")
            )

        if self._choice(FeatureAxis.LOGGING) == LoggingChoice.STRUCTURED:
            modules[f"{self.package_dir}/logging_config.py"] = self._render_module(
                "logging/structured.py.j2", title="Structured Logging Configuration"
            )

        return modules

    def generate_migration_files(self) -> Dict[str, str]:
        """
        Generate the Alembic migration environment.

        Only relational databases get one — Alembic has nothing to migrate on
        MongoDB or Redis, so the selection is silently ignored there.

        Returns:
            Mapping of project-relative path to file content
        """
        if self._choice(FeatureAxis.MIGRATIONS) != MigrationsChoice.ALEMBIC:
            return {}
        if not self._uses_sql_database:
            return {}

        # Derived from the project, not random: ``planned_files()`` and
        # ``generate_all_files()`` must agree on the filename, and
        # regenerating a project must not churn the revision id.
        revision_id = hashlib.sha256(
            f"{self.config.get('project_name', '')}:{self._database_type}".encode()
        ).hexdigest()[:12]
        return {
            "alembic.ini": self._render_module(
                "migrations/alembic_ini.j2",
                title="Alembic configuration",
                database_url=SQLALCHEMY_URLS[self._database_type],
            ),
            "alembic/env.py": self._render_module(
                "migrations/env.py.j2", title="Alembic environment"
            ),
            "alembic/script.py.mako": self._render_module(
                "migrations/script.py.mako.j2"
            ),
            f"alembic/versions/{revision_id}_initial.py": self._render_module(
                "migrations/initial_revision.py.j2", revision_id=revision_id
            ),
            "scripts/migrate.sh": self._render_module("migrations/migrate_sh.j2"),
        }

    def generate_tooling_files(self) -> Dict[str, str]:
        """
        Generate the developer-tooling files for the ``tooling`` selection.

        The ruff configuration is not returned here: it is merged into the
        project's ``pyproject.toml`` by :meth:`apply_ruff_configuration`
        rather than written as a standalone file.

        Returns:
            Mapping of project-relative path to file content
        """
        selected = self._choices(FeatureAxis.TOOLING)
        if not selected:
            return {}

        with_ruff = self._uses_ruff
        files: Dict[str, str] = {}

        if ToolingChoice.PRE_COMMIT in selected:
            files[".pre-commit-config.yaml"] = self._render_module(
                "tooling/pre_commit.j2", with_ruff=with_ruff
            )
        if ToolingChoice.GITHUB_ACTIONS in selected:
            files[".github/workflows/test.yml"] = self._render_module(
                "tooling/github_actions.j2", with_ruff=with_ruff
            )
        if ToolingChoice.DEVCONTAINER in selected:
            files[".devcontainer/devcontainer.json"] = self._render_module(
                "tooling/devcontainer.j2", with_ruff=with_ruff
            )
        if ToolingChoice.MAKEFILE in selected:
            files["Makefile"] = self._render_module(
                "tooling/makefile.j2", with_ruff=with_ruff
            )

        return files

    def generate_ruff_config(self) -> str:
        """
        Render the ``[tool.ruff]`` block appended to ``pyproject.toml``.

        Returns:
            TOML snippet configuring ruff's linter and formatter
        """
        return self._render_module("tooling/ruff_toml.j2")

    def apply_ruff_configuration(self) -> str:
        """
        Merge the ruff configuration into the project's ``pyproject.toml``.

        ruff replaces black + isort, so its settings belong next to the rest
        of the project metadata. When the layout has no ``pyproject.toml``
        (a ``pip`` / ``requirements.txt`` project), a standalone
        ``ruff.toml`` is written instead.

        Returns:
            Project-relative path of the file that received the configuration
        """
        snippet = self.generate_ruff_config()
        pyproject = self.project_dir / "pyproject.toml"

        if pyproject.exists():
            existing = pyproject.read_text(encoding="utf-8")
            if "[tool.ruff]" not in existing:
                if not existing.endswith("\n"):
                    existing += "\n"
                pyproject.write_text(existing + snippet, encoding="utf-8")
            return "pyproject.toml"

        # ``ruff.toml`` uses bare top-level keys, not ``[tool.ruff]`` tables.
        standalone = snippet.replace("[tool.ruff.", "[").replace("[tool.ruff]\n", "")
        ruff_toml = self.project_dir / "ruff.toml"
        ruff_toml.write_text(standalone.lstrip("\n"), encoding="utf-8")
        return "ruff.toml"

    def generate_testing_files(self) -> Dict[str, str]:
        """
        Generate the extra test scaffolding for the ``Advanced`` tier.

        Returns:
            Mapping of project-relative path to file content
        """
        if self._choice(FeatureAxis.TESTING) != TestingChoice.ADVANCED:
            return {}

        return {
            "tests/factories.py": self._render_module(
                "test/factories.py.j2", title="Test data factories"
            ),
            "tests/test_factories.py": self._render_module(
                "test/test_factories.py.j2", title="Factory smoke tests"
            ),
        }

    def generate_docker_files(self, app_module: str = "src.main:app") -> List[str]:
        """Generate Dockerfile and docker-compose.yml.

        The ``app_module`` is the ``module:attr`` string baked into the
        Dockerfile's ``CMD``. Architecture presets that put the FastAPI app
        at a non-default location (e.g. ``domain-starter`` ships
        ``src/app/main.py``) must pass the matching dotted path so the
        generated container actually starts.

        Returns:
            Project-relative paths that were written
        """
        deployment = self.config.get("deployment", [])
        written: List[str] = []

        if "Docker" in deployment:
            dockerfile_path = self.project_dir / "Dockerfile"
            dockerfile_path.write_text(
                self._generate_dockerfile(app_module=app_module), encoding="utf-8"
            )
            written.append("Dockerfile")

        if "docker-compose" in deployment:
            compose_path = self.project_dir / "docker-compose.yml"
            compose_path.write_text(self._generate_docker_compose(), encoding="utf-8")
            written.append("docker-compose.yml")

        return written

    def _generate_dockerfile(self, app_module: str = "src.main:app") -> str:
        """Generate Dockerfile content with a layout-aware uvicorn target."""
        return self._render(
            "docker/dockerfile.j2",
            title="Dockerfile",
            cmd=["uvicorn", app_module, "--host", "0.0.0.0", "--port", "8000"],
        )

    def _generate_docker_compose(self) -> str:
        """Generate docker-compose.yml content."""
        db_service = COMPOSE_DB_SERVICES.get(self._database_type)
        redis_service = self._needs_redis_service

        # A Redis *database* selection and a Redis *cache/broker* selection
        # collapse onto the same compose service — never declare it twice.
        if db_service == "redis":
            db_service = None
            redis_service = True

        depends_on: List[str] = []
        volumes: List[str] = []
        if db_service:
            depends_on.append(db_service)
            volume = _COMPOSE_DB_VOLUMES.get(db_service)
            if volume:
                volumes.append(volume)
        if redis_service:
            depends_on.append("redis")
            volumes.append("redis_data")

        return self._render(
            "docker/docker_compose.j2",
            title="docker-compose.yml",
            db_service=db_service,
            redis_service=redis_service,
            worker_command=self._worker_command(),
            depends_on=depends_on,
            volumes=volumes,
        )

    def generate_test_config(self) -> Optional[str]:
        """
        Generate pytest configuration.

        Returns:
            Content of pytest.ini or None
        """
        testing_type = self._choice(FeatureAxis.TESTING)

        if testing_type == NONE_CHOICE:
            return None

        with_coverage = (
            TestingChoice.COVERAGE in testing_type
            or TestingChoice.ADVANCED in testing_type
        )
        return self._render(
            "test/pytest_ini.j2",
            title="pytest configuration",
            with_coverage=with_coverage,
        )


__all__ = [
    "COMPOSE_DB_SERVICES",
    "DEFAULT_AUTH_CONFIG_RELPATH",
    "DEFAULT_DB_CONFIG_RELPATH",
    "DEFAULT_MAIN_RELPATH",
    "DynamicConfigGenerator",
    "SQLALCHEMY_URLS",
    "SQL_DATABASES",
    "get_environment",
]
