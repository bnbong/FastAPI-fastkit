# --------------------------------------------------------------------------
# Test cases for backend/project_builder/config_generator.py
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import ast
import itertools
import json
import tempfile
from pathlib import Path

from fastapi_fastkit.backend.project_builder.config_generator import (
    DynamicConfigGenerator,
)


class TestDynamicConfigGeneratorInitialization:
    """Test cases for DynamicConfigGenerator initialization."""

    def test_initialization_with_config(self) -> None:
        """Test DynamicConfigGenerator initialization."""
        # given
        config = {"project_name": "test-project"}
        project_dir = "/tmp/test-project"

        # when
        generator = DynamicConfigGenerator(config, project_dir)

        # then
        assert generator.config is not None
        assert generator.project_dir.name == "test-project"


class TestGenerateMainPy:
    """Test cases for generate_main_py method."""

    def test_generate_main_py_minimal(self) -> None:
        """Test generating main.py with minimal configuration."""
        # given
        config = {
            "project_name": "TestProject",
            "description": "A test project",
            "database": {"type": "None"},
            "authentication": "None",
            "monitoring": "None",
            "utilities": [],
        }
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_main_py()

        # then
        assert "from fastapi import FastAPI" in content
        assert "from fastapi.middleware.cors import CORSMiddleware" in content
        assert 'title="TestProject"' in content
        assert 'description="A test project"' in content
        assert '@app.get("/", tags=["Health"])' in content
        assert "async def root()" in content
        assert '@app.get("/health", tags=["Health"])' in content
        # Modernized: lifespan context manager, never the removed on_event hook.
        assert "@asynccontextmanager" in content
        assert "lifespan=lifespan" in content
        assert "on_event" not in content
        # addroute anchors (BRIEF contract).
        assert "# fastkit:imports" in content
        assert "# fastkit:routes" in content

    def test_generate_main_py_with_postgresql(self) -> None:
        """Test generating main.py with PostgreSQL database."""
        # given
        config = {
            "project_name": "TestProject",
            "description": "Test",
            "database": {"type": "PostgreSQL"},
            "authentication": "None",
            "monitoring": "None",
            "utilities": [],
        }
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_main_py()

        # then
        assert (
            "from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine"
            in content
        )
        assert "from sqlalchemy.orm import sessionmaker" in content

    def test_generate_main_py_with_mongodb(self) -> None:
        """Test generating main.py with MongoDB database."""
        # given
        config = {
            "project_name": "TestProject",
            "description": "Test",
            "database": {"type": "MongoDB"},
            "authentication": "None",
            "monitoring": "None",
            "utilities": [],
        }
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_main_py()

        # then
        assert "from motor.motor_asyncio import AsyncIOMotorClient" in content

    def test_generate_main_py_with_jwt_auth(self) -> None:
        """Test generating main.py with JWT authentication."""
        # given
        config = {
            "project_name": "TestProject",
            "description": "Test",
            "database": {"type": "None"},
            "authentication": "JWT",
            "monitoring": "None",
            "utilities": [],
        }
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_main_py()

        # then
        # JWT imports HTTPBearer security
        assert "HTTPBearer" in content or "Security" in content

    def test_generate_main_py_with_cors_utility(self) -> None:
        """Test generating main.py with CORS utility."""
        # given
        config = {
            "project_name": "TestProject",
            "description": "Test",
            "database": {"type": "None"},
            "authentication": "None",
            "monitoring": "None",
            "utilities": ["CORS"],
        }
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_main_py()

        # then
        assert "CORSMiddleware" in content
        assert "allow_origins" in content

    def test_generate_main_py_with_rate_limiting(self) -> None:
        """Test generating main.py with rate limiting."""
        # given
        config = {
            "project_name": "TestProject",
            "description": "Test",
            "database": {"type": "None"},
            "authentication": "None",
            "monitoring": "None",
            "utilities": ["Rate-Limiting"],
        }
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_main_py()

        # then
        assert "Limiter" in content or "slowapi" in content

    def test_generate_main_py_with_prometheus(self) -> None:
        """Test generating main.py with Prometheus monitoring."""
        # given
        config = {
            "project_name": "TestProject",
            "description": "Test",
            "database": {"type": "None"},
            "authentication": "None",
            "monitoring": "Prometheus",
            "utilities": [],
        }
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_main_py()

        # then
        assert "Instrumentator" in content or "prometheus" in content.lower()


class TestGenerateDatabaseConfig:
    """Test cases for generate_database_config method."""

    def test_generate_database_config_none(self) -> None:
        """Test that None database returns None config."""
        # given
        config = {"database": {"type": "None"}}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_database_config()

        # then
        assert content is None

    def test_generate_database_config_postgresql(self) -> None:
        """Test generating PostgreSQL database config."""
        # given
        config = {"database": {"type": "PostgreSQL"}}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_database_config()

        # then
        assert content is not None
        assert "Database Configuration" in content
        assert "SQLAlchemy" in content or "sqlalchemy" in content
        assert "postgresql+asyncpg" in content
        assert "AsyncSession" in content

    def test_generate_database_config_mysql(self) -> None:
        """Test generating MySQL database config."""
        # given
        config = {"database": {"type": "MySQL"}}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_database_config()

        # then
        assert content is not None
        assert "mysql+aiomysql" in content

    def test_generate_database_config_sqlite(self) -> None:
        """Test generating SQLite database config."""
        # given
        config = {"database": {"type": "SQLite"}}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_database_config()

        # then
        assert content is not None
        assert "sqlite+aiosqlite" in content

    def test_generate_database_config_mongodb(self) -> None:
        """Test generating MongoDB database config."""
        # given
        config = {"database": {"type": "MongoDB"}}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_database_config()

        # then
        assert content is not None
        assert "MongoDB Configuration" in content
        assert "motor" in content.lower()


class TestGenerateAuthConfig:
    """Test cases for generate_auth_config method."""

    def test_generate_auth_config_none(self) -> None:
        """Test that None authentication returns None."""
        # given
        config = {"authentication": "None"}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_auth_config()

        # then
        assert content is None

    def test_generate_auth_config_jwt(self) -> None:
        """Test generating JWT authentication config."""
        # given
        config = {"authentication": "JWT"}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_auth_config()

        # then
        assert content is not None
        assert "JWT Authentication Configuration" in content
        assert "jose" in content.lower()
        assert "passlib" in content or "password" in content.lower()
        assert "SECRET_KEY" in content

    def test_generate_auth_config_fastapi_users(self) -> None:
        """Test generating FastAPI-Users authentication config."""
        # given
        config = {"authentication": "FastAPI-Users"}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_auth_config()

        # then
        assert content is not None
        assert "FastAPI-Users" in content


class TestGenerateTestConfig:
    """Test cases for generate_test_config method."""

    def test_generate_test_config_none(self) -> None:
        """Test that None testing returns None."""
        # given
        config = {"testing": "None"}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_test_config()

        # then
        assert content is None

    def test_generate_test_config_basic(self) -> None:
        """Test generating basic pytest config."""
        # given
        config = {"testing": "Basic"}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_test_config()

        # then
        assert content is not None
        assert "[pytest]" in content
        assert "testpaths = tests" in content

    def test_generate_test_config_coverage(self) -> None:
        """Test generating pytest config with coverage."""
        # given
        config = {"testing": "Coverage"}
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_test_config()

        # then
        assert content is not None
        assert "[coverage:run]" in content


class TestGenerateDockerFiles:
    """Test cases for generate_docker_files method."""

    def test_generated_dockerfile_uses_exec_form_cmd(self) -> None:
        """Dockerfile CMD must be JSON exec form, not shell form with single quotes."""
        # given
        with tempfile.TemporaryDirectory() as tmp:
            config = {"deployment": ["Docker"]}
            generator = DynamicConfigGenerator(config, tmp)

            # when
            generator.generate_docker_files()

            # then
            dockerfile = Path(tmp) / "Dockerfile"
            assert dockerfile.exists()
            content = dockerfile.read_text()

            # Find the CMD line and validate it parses as JSON array (exec form)
            cmd_lines = [
                line for line in content.splitlines() if line.startswith("CMD ")
            ]
            assert len(cmd_lines) == 1
            cmd_payload = cmd_lines[0][len("CMD ") :]

            # Single quotes are Docker shell form; exec form requires double quotes.
            assert "'" not in cmd_payload, (
                "Generated Dockerfile CMD still uses single quotes (shell form): "
                f"{cmd_payload!r}"
            )
            parsed = json.loads(cmd_payload)
            assert parsed[0] == "uvicorn"
            assert "src.main:app" in parsed

    def test_generated_dockerfile_honors_custom_app_module(self) -> None:
        """The Dockerfile CMD must target the caller-supplied app module.

        Regression for the Codex P1 finding on PR #55: domain-starter
        ships ``src/app/main.py``, so the default ``src.main:app`` would
        produce a container that fails at startup. Callers (like the
        interactive init flow, via ``PresetLayoutStrategist.app_module``)
        thread the layout-correct module through ``generate_docker_files``.
        """
        # given
        with tempfile.TemporaryDirectory() as tmp:
            config = {"deployment": ["Docker"]}
            generator = DynamicConfigGenerator(config, tmp)

            # when
            generator.generate_docker_files(app_module="src.app.main:app")

            # then
            dockerfile = Path(tmp) / "Dockerfile"
            content = dockerfile.read_text()
            cmd_lines = [
                line for line in content.splitlines() if line.startswith("CMD ")
            ]
            assert len(cmd_lines) == 1
            parsed = json.loads(cmd_lines[0][len("CMD ") :])
            assert "src.app.main:app" in parsed
            # The bogus default must not leak in alongside the override.
            assert "src.main:app" not in parsed


class TestHelperMethods:
    """Test cases for helper methods."""

    def test_build_header(self) -> None:
        """Test _build_header static method."""
        # given
        title = "Test File"

        # when
        header = DynamicConfigGenerator._build_header(title)

        # then
        assert isinstance(header, list)
        assert "Test File" in header[1]
        assert "FastAPI-fastkit" in header[2]

    def test_join_lines(self) -> None:
        """Test _join_lines static method."""
        # given
        lines = ["line1", "line2", "line3"]

        # when
        result = DynamicConfigGenerator._join_lines(lines)

        # then
        assert "line1\nline2\nline3\n" == result

    def test_build_code_block(self) -> None:
        """Test _build_code_block static method."""
        # given
        indent = "    "
        lines = ("line1", "line2")

        # when
        result = DynamicConfigGenerator._build_code_block(indent, *lines)

        # then
        assert result == ["    line1", "    line2"]


class TestRenderedOutputIsValidPython:
    """Every rendered Python artifact must parse.

    Covers the full feature matrix (database x auth x docker x monitoring)
    so a broken fragment fails here instead of in a generated project.
    """

    DATABASES = ["None", "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis"]
    AUTHS = ["None", "JWT", "FastAPI-Users", "OAuth2", "Session-based"]
    MONITORING = ["None", "Loguru", "Prometheus", "OpenTelemetry"]
    ASYNC_TASKS = ["None", "Celery", "Dramatiq"]

    def test_all_feature_combinations_render_valid_python(self) -> None:
        """Every artifact of every combination parses and stays coherent."""
        combinations = itertools.product(
            self.DATABASES,
            self.AUTHS,
            [True, False],
            self.MONITORING,
            self.ASYNC_TASKS,
        )

        for db, auth, with_docker, monitoring, tasks in combinations:
            # given
            config = {
                "project_name": "MatrixProject",
                "description": "Matrix test",
                "database": {"type": db},
                "authentication": auth,
                "monitoring": monitoring,
                "async_tasks": tasks,
                "caching": "Redis",
                "logging": "structured",
                "migrations": "Alembic",
                "utilities": ["CORS", "Rate-Limiting", "WebSocket", "Pagination"],
                "tooling": ["ruff", "pre-commit", "makefile"],
                "deployment": ["Docker", "docker-compose"] if with_docker else [],
                "testing": "Advanced",
            }

            label = f"{db}/{auth}/{with_docker}/{monitoring}/{tasks}"

            with tempfile.TemporaryDirectory() as tmp:
                generator = DynamicConfigGenerator(config, tmp)

                # when
                written = generator.generate_all_files()

                # then — every generated Python module is syntactically valid
                for relative in written:
                    if relative.endswith(".py"):
                        ast.parse(
                            (Path(tmp) / relative).read_text(),
                            filename=f"{label}:{relative}",
                        )

                main_py = (Path(tmp) / "src/main.py").read_text()
                assert "# fastkit:imports" in main_py, label
                assert "# fastkit:routes" in main_py, label
                assert '@app.get("/health", tags=["Health"])' in main_py, label
                assert '@app.get("/ready", tags=["Health"])' in main_py, label
                assert "on_event" not in main_py, label

                # Every router the app mounts must have been generated.
                for module, path in (
                    ("tasks", "src/features/tasks.py"),
                    ("cache", "src/features/cache.py"),
                    ("websocket", "src/features/websocket.py"),
                    ("pagination", "src/features/pagination.py"),
                ):
                    if f"{module}_router" in main_py:
                        assert path in written, f"{label}: {path} not generated"

                dockerfile = Path(tmp) / "Dockerfile"
                compose = Path(tmp) / "docker-compose.yml"
                assert dockerfile.exists() is with_docker, label
                assert compose.exists() is with_docker, label
                if with_docker:
                    assert "FROM python:3.12-slim" in dockerfile.read_text(), label
                    compose_text = compose.read_text()
                    # Caching is always Redis here, so the service is mandatory.
                    assert "redis:" in compose_text, label
                    if tasks != "None":
                        assert "worker:" in compose_text, label

    def test_project_name_with_quotes_is_escaped(self) -> None:
        """A hostile project name must not break the rendered module."""
        # given
        config = {
            "project_name": 'Weird "Quoted" Name',
            "description": "line1\nline2",
            "database": {"type": "None"},
            "authentication": "None",
            "monitoring": "None",
            "utilities": [],
        }
        generator = DynamicConfigGenerator(config, "/tmp/test")

        # when
        content = generator.generate_main_py()

        # then
        ast.parse(content)

    def test_test_config_renders_for_every_testing_choice(self) -> None:
        """pytest config renders (or is skipped) for each testing option."""
        # given / when / then
        for testing in ["None", "Basic", "Coverage", "Advanced"]:
            generator = DynamicConfigGenerator({"testing": testing}, "/tmp/test")
            content = generator.generate_test_config()

            if testing == "None":
                assert content is None
            else:
                assert content is not None
                assert "[pytest]" in content


class TestFeatureModuleGeneration:
    """Every catalog choice must produce real, importable code.

    Before #57 the interactive catalog offered selections (Celery, caching,
    WebSocket, OAuth2, ...) that installed packages but generated nothing —
    a "false promise". These tests pin each one to an actual artifact.
    """

    @staticmethod
    def _generate(**overrides: object) -> dict:
        """Render every artifact for a config, keyed by relative path."""
        config = {
            "project_name": "FeatureProject",
            "description": "Feature coverage",
            "database": {"type": "None"},
            "authentication": "None",
            "utilities": [],
        }
        config.update(overrides)
        return DynamicConfigGenerator(config, "/tmp/test").build_artifacts()

    def test_celery_generates_worker_and_task_routes(self) -> None:
        """Celery must ship a worker module and the submit/poll routes."""
        # given / when
        artifacts = self._generate(async_tasks="Celery")

        # then
        worker = artifacts["src/worker.py"]
        routes = artifacts["src/features/tasks.py"]
        ast.parse(worker)
        ast.parse(routes)
        assert "Celery(" in worker
        assert "autoretry_for=(Exception,)" in worker
        assert "max_retries=3" in worker
        assert 'APIRouter(prefix="/api/v1/tasks"' in routes
        assert "example_task.delay" in routes
        assert "AsyncResult" in routes

    def test_dramatiq_generates_equivalent_worker_and_routes(self) -> None:
        """Dramatiq must reach the same shape as the Celery option."""
        # given / when
        artifacts = self._generate(async_tasks="Dramatiq")

        # then
        worker = artifacts["src/worker.py"]
        routes = artifacts["src/features/tasks.py"]
        ast.parse(worker)
        ast.parse(routes)
        assert "RedisBroker" in worker
        assert "@dramatiq.actor" in worker
        assert 'APIRouter(prefix="/api/v1/tasks"' in routes
        assert "example_task.send" in routes

    def test_async_tasks_add_worker_and_redis_compose_services(self) -> None:
        """docker-compose must run the worker beside the API."""
        # given
        config = {
            "project_name": "P",
            "database": {"type": "PostgreSQL"},
            "async_tasks": "Celery",
            "deployment": ["Docker", "docker-compose"],
        }

        # when
        with tempfile.TemporaryDirectory() as tmp:
            DynamicConfigGenerator(config, tmp).generate_docker_files()
            compose = (Path(tmp) / "docker-compose.yml").read_text()

        # then
        assert "worker:" in compose
        assert "src.worker.celery_app" in compose
        assert "redis:" in compose
        assert "image: redis:7-alpine" in compose

    def test_caching_initializes_backend_and_ships_cached_endpoint(self) -> None:
        """Redis caching must be initialised in lifespan and demonstrated."""
        # given / when
        artifacts = self._generate(caching="Redis")

        # then
        main_py = artifacts["src/main.py"]
        cache_module = artifacts["src/features/cache.py"]
        ast.parse(main_py)
        ast.parse(cache_module)
        assert "FastAPICache.init(RedisBackend(" in main_py
        assert "from fastapi_cache import FastAPICache" in main_py
        assert "@cache(expire=60)" in cache_module

    def test_websocket_utility_generates_connection_manager(self) -> None:
        """The WebSocket utility must produce a real /ws endpoint."""
        # given / when
        artifacts = self._generate(utilities=["WebSocket"])

        # then
        module = artifacts["src/features/websocket.py"]
        ast.parse(module)
        assert "class ConnectionManager" in module
        assert '@router.websocket("/ws")' in module
        assert "async def broadcast" in module
        assert "app.include_router(websocket_router)" in artifacts["src/main.py"]

    def test_pagination_utility_calls_add_pagination(self) -> None:
        """Pagination is inert unless ``add_pagination(app)`` is called."""
        # given / when
        artifacts = self._generate(utilities=["Pagination"])

        # then
        module = artifacts["src/features/pagination.py"]
        ast.parse(module)
        assert "Page[Item]" in module
        assert "add_pagination(app)" in artifacts["src/main.py"]

    def test_opentelemetry_instruments_the_app(self) -> None:
        """OpenTelemetry must instrument the app and configure an exporter."""
        # given / when
        artifacts = self._generate(monitoring="OpenTelemetry")

        # then
        main_py = artifacts["src/main.py"]
        ast.parse(main_py)
        assert "FastAPIInstrumentor.instrument_app(app" in main_py
        assert "OTLPSpanExporter" in main_py
        assert "OTEL_EXPORTER_OTLP_ENDPOINT" in main_py

    def test_oauth2_generates_provider_routes_and_session_middleware(self) -> None:
        """OAuth2 must produce Google/GitHub routes plus session wiring."""
        # given / when
        artifacts = self._generate(authentication="OAuth2")

        # then
        auth_module = artifacts["src/config/auth.py"]
        main_py = artifacts["src/main.py"]
        ast.parse(auth_module)
        ast.parse(main_py)
        assert 'oauth.register(\n    name="google"' in auth_module
        assert 'name="github"' in auth_module
        assert '@router.get("/login/{provider}")' in auth_module
        assert "app.add_middleware(SessionMiddleware" in main_py

    def test_session_auth_generates_login_logout(self) -> None:
        """Session-based auth must produce a working login/logout cycle."""
        # given / when
        artifacts = self._generate(authentication="Session-based")

        # then
        auth_module = artifacts["src/config/auth.py"]
        main_py = artifacts["src/main.py"]
        ast.parse(auth_module)
        ast.parse(main_py)
        assert '@router.post("/login")' in auth_module
        assert '@router.post("/logout")' in auth_module
        assert "request.session" in auth_module
        assert "SessionMiddleware" in main_py

    def test_redis_database_generates_async_client(self) -> None:
        """Selecting Redis as the database must yield a client module."""
        # given / when
        artifacts = self._generate(database={"type": "Redis"})

        # then
        module = artifacts["src/config/database.py"]
        ast.parse(module)
        assert "import redis.asyncio as redis" in module
        assert "async def get_redis(" in module

    def test_mysql_gets_a_compose_service(self) -> None:
        """MySQL used to be silently dropped from docker-compose."""
        # given
        config = {
            "project_name": "P",
            "database": {"type": "MySQL"},
            "deployment": ["Docker", "docker-compose"],
        }

        # when
        with tempfile.TemporaryDirectory() as tmp:
            DynamicConfigGenerator(config, tmp).generate_docker_files()
            compose = (Path(tmp) / "docker-compose.yml").read_text()

        # then
        assert "mysql:" in compose
        assert "image: mysql:8" in compose
        assert "mysql_data" in compose

    def test_advanced_testing_generates_factories(self) -> None:
        """The Advanced tier promises factory-boy/faker fixtures."""
        # given / when
        artifacts = self._generate(testing="Advanced")

        # then
        factories = artifacts["tests/factories.py"]
        tests = artifacts["tests/test_factories.py"]
        ast.parse(factories)
        ast.parse(tests)
        assert "class UserFactory(factory.Factory)" in factories
        assert "Faker()" in factories
        assert "from tests.factories import" in tests

    def test_structured_logging_generates_json_logger_and_request_id(self) -> None:
        """Structured logging must ship both the formatter and middleware."""
        # given / when
        artifacts = self._generate(logging="structured")

        # then
        module = artifacts["src/logging_config.py"]
        main_py = artifacts["src/main.py"]
        ast.parse(module)
        ast.parse(main_py)
        assert "class JsonFormatter(logging.Formatter)" in module
        assert "class RequestIDMiddleware" in module
        assert "X-Request-ID" in module
        assert "app.add_middleware(RequestIDMiddleware)" in main_py

    def test_health_and_ready_endpoints_are_always_generated(self) -> None:
        """Both probes ship regardless of the feature selection."""
        # given / when
        artifacts = self._generate()

        # then
        main_py = artifacts["src/main.py"]
        assert '@app.get("/health", tags=["Health"])' in main_py
        assert '@app.get("/ready", tags=["Health"])' in main_py

    def test_generated_main_py_imports_are_isort_ordered(self) -> None:
        """Fragments compose freely, so the generator has to sort imports."""
        # given / when
        artifacts = self._generate(
            database={"type": "PostgreSQL"},
            authentication="OAuth2",
            async_tasks="Celery",
            caching="Redis",
            monitoring="OpenTelemetry",
            logging="structured",
            utilities=["CORS", "Rate-Limiting", "WebSocket", "Pagination"],
        )

        # then — first-party imports come last, and each block is sorted.
        main_py = artifacts["src/main.py"]
        body = main_py.split("# fastkit:imports")[0]
        blocks = [
            block.strip().splitlines()
            for block in body.split("\n\n")
            if block.strip().startswith(("import ", "from "))
        ]
        assert len(blocks) == 3, main_py
        for block in blocks:
            assert block == sorted(
                block, key=lambda line: (not line.startswith("import "), line)
            ), block
        assert all(line.startswith("from src.") for line in blocks[-1])


class TestMigrationsAndTooling:
    """Coverage for the axes added in #57."""

    @staticmethod
    def _generate(**overrides: object) -> dict:
        config = {
            "project_name": "ToolProject",
            "description": "Tooling coverage",
            "database": {"type": "PostgreSQL"},
            "authentication": "None",
            "utilities": [],
        }
        config.update(overrides)
        return DynamicConfigGenerator(config, "/tmp/test").build_artifacts()

    def test_alembic_generates_async_environment(self) -> None:
        """Alembic must be wired for SQLAlchemy's async engine."""
        # given / when
        artifacts = self._generate(migrations="Alembic")

        # then
        env_py = artifacts["alembic/env.py"]
        ast.parse(env_py)
        assert "async_engine_from_config" in env_py
        assert "asyncio.run(run_async_migrations())" in env_py
        assert "script_location = alembic" in artifacts["alembic.ini"]
        assert "alembic upgrade" in artifacts["scripts/migrate.sh"]

        initial = next(
            content
            for path, content in artifacts.items()
            if path.startswith("alembic/versions/")
        )
        ast.parse(initial)
        assert "down_revision: str | None = None" in initial

    def test_alembic_is_skipped_without_a_relational_database(self) -> None:
        """MongoDB has no schema for Alembic to migrate."""
        # given / when
        artifacts = self._generate(migrations="Alembic", database={"type": "MongoDB"})

        # then
        assert not any(path.startswith("alembic") for path in artifacts)

    def test_each_tooling_option_produces_its_file(self) -> None:
        """Every tooling checkbox maps to exactly one generated file."""
        # given
        expected = {
            "pre-commit": ".pre-commit-config.yaml",
            "github-actions": ".github/workflows/test.yml",
            "devcontainer": ".devcontainer/devcontainer.json",
            "makefile": "Makefile",
        }

        # when / then
        for choice, path in expected.items():
            artifacts = self._generate(tooling=[choice])
            assert path in artifacts, choice

    def test_generated_ci_workflow_pins_python_312(self) -> None:
        """The repo standardises on Python 3.12; CI must match."""
        # given / when
        workflow = self._generate(tooling=["github-actions"])[
            ".github/workflows/test.yml"
        ]

        # then
        assert 'python-version: "3.12"' in workflow
        assert "pytest" in workflow

    def test_makefile_exposes_the_documented_targets(self) -> None:
        """install/test/lint/format/run are the advertised entry points."""
        # given / when
        makefile = self._generate(tooling=["makefile"])["Makefile"]

        # then
        for target in ("install:", "test:", "lint:", "format:", "run:"):
            assert target in makefile, target
        assert "src.main:app" in makefile

    def test_devcontainer_is_valid_json(self) -> None:
        """A malformed devcontainer.json silently breaks the whole feature."""
        # given / when
        content = self._generate(tooling=["devcontainer"])[
            ".devcontainer/devcontainer.json"
        ]

        # then
        parsed = json.loads(content)
        assert parsed["image"] == "mcr.microsoft.com/devcontainers/python:3.12"

    def test_ruff_configuration_is_merged_into_pyproject(self) -> None:
        """ruff replaces black+isort, so its config belongs in pyproject."""
        # given
        config = {
            "project_name": "P",
            "database": {"type": "None"},
            "tooling": ["ruff"],
        }

        # when
        with tempfile.TemporaryDirectory() as tmp:
            pyproject = Path(tmp) / "pyproject.toml"
            pyproject.write_text('[project]\nname = "p"\n')
            target = DynamicConfigGenerator(config, tmp).apply_ruff_configuration()
            content = pyproject.read_text()

        # then
        assert target == "pyproject.toml"
        assert '[project]\nname = "p"' in content
        assert "[tool.ruff]" in content
        assert 'target-version = "py312"' in content
        assert "[tool.ruff.format]" in content

    def test_ruff_falls_back_to_a_standalone_file(self) -> None:
        """A requirements.txt-only project still gets ruff configured."""
        # given
        config = {"project_name": "P", "database": {"type": "None"}}

        # when
        with tempfile.TemporaryDirectory() as tmp:
            target = DynamicConfigGenerator(config, tmp).apply_ruff_configuration()
            content = (Path(tmp) / "ruff.toml").read_text()

        # then
        assert target == "ruff.toml"
        assert "[tool.ruff]" not in content
        assert 'target-version = "py312"' in content

    def test_pre_commit_swaps_black_for_ruff_when_ruff_is_selected(self) -> None:
        """The two formatter choices must not both be configured."""
        # given / when
        with_ruff = self._generate(tooling=["pre-commit", "ruff"])[
            ".pre-commit-config.yaml"
        ]
        without_ruff = self._generate(tooling=["pre-commit"])[".pre-commit-config.yaml"]

        # then
        assert "ruff-pre-commit" in with_ruff
        assert "psf/black" not in with_ruff
        assert "psf/black" in without_ruff
        assert "ruff" not in without_ruff


class TestGenerateAllFiles:
    """``generate_all_files`` is the single write-everything entry point."""

    FULL_CONFIG = {
        "project_name": "Everything App",
        "description": "All features at once",
        "database": {"type": "PostgreSQL"},
        "authentication": "JWT",
        "async_tasks": "Celery",
        "caching": "Redis",
        "monitoring": "Prometheus",
        "logging": "structured",
        "testing": "Advanced",
        "migrations": "Alembic",
        "utilities": ["CORS", "Rate-Limiting", "WebSocket", "Pagination"],
        "tooling": ["ruff", "pre-commit", "github-actions", "devcontainer", "makefile"],
        "deployment": ["Docker", "docker-compose"],
    }

    def test_writes_every_artifact_to_disk(self) -> None:
        """Everything the config implies lands under the project directory."""
        # given
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "pyproject.toml").write_text('[project]\nname = "p"\n')
            generator = DynamicConfigGenerator(self.FULL_CONFIG, tmp)

            # when
            written = generator.generate_all_files()

            # then
            for relative in written:
                target = Path(tmp) / relative
                assert target.exists(), relative
                if relative.endswith(".py"):
                    ast.parse(target.read_text(), filename=relative)

            for expected in (
                "src/main.py",
                "src/worker.py",
                "src/features/tasks.py",
                "src/features/cache.py",
                "src/features/websocket.py",
                "src/features/pagination.py",
                "src/features/__init__.py",
                "src/logging_config.py",
                "src/config/database.py",
                "src/config/auth.py",
                "alembic/env.py",
                "scripts/migrate.sh",
                "Makefile",
                "Dockerfile",
                "docker-compose.yml",
                "pytest.ini",
                "tests/factories.py",
            ):
                assert expected in written, expected

    def test_migrate_script_is_executable(self) -> None:
        """``scripts/migrate.sh`` is useless without the executable bit."""
        # given
        with tempfile.TemporaryDirectory() as tmp:
            generator = DynamicConfigGenerator(self.FULL_CONFIG, tmp)

            # when
            generator.generate_all_files()

            # then
            mode = (Path(tmp) / "scripts" / "migrate.sh").stat().st_mode
            assert mode & 0o111, oct(mode)

    def test_planned_files_matches_what_gets_written(self) -> None:
        """``--dry-run`` must not lie about what a real run produces."""
        # given
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "pyproject.toml").write_text('[project]\nname = "p"\n')
            generator = DynamicConfigGenerator(self.FULL_CONFIG, tmp)

            # when
            planned = generator.planned_files()
            written = generator.generate_all_files()

            # then
            assert planned == written

    def test_include_main_false_preserves_the_template_entrypoint(self) -> None:
        """Presets that keep their shipped main.py must not have it clobbered."""
        # given
        with tempfile.TemporaryDirectory() as tmp:
            main_py = Path(tmp) / "src" / "main.py"
            main_py.parent.mkdir(parents=True)
            main_py.write_text("# template-shipped\n")
            generator = DynamicConfigGenerator(self.FULL_CONFIG, tmp)

            # when
            written = generator.generate_all_files(include_main=False)

            # then
            assert "src/main.py" not in written
            assert main_py.read_text() == "# template-shipped\n"

    def test_layout_paths_flow_into_generated_imports(self) -> None:
        """A domain-starter layout must import from ``src.app``, not ``src``."""
        # given
        with tempfile.TemporaryDirectory() as tmp:
            generator = DynamicConfigGenerator(
                self.FULL_CONFIG,
                tmp,
                app_module="src.app.main:app",
                main_py_relpath="src/app/main.py",
                db_config_relpath="src/app/core/database.py",
                auth_config_relpath="src/app/core/auth.py",
            )

            # when
            written = generator.generate_all_files()

            # then
            assert "src/app/worker.py" in written
            assert "src/app/features/tasks.py" in written
            assert "src/app/core/database.py" in written
            routes = (Path(tmp) / "src/app/features/tasks.py").read_text()
            assert "from src.app.worker import" in routes
            main_py = (Path(tmp) / "src/app/main.py").read_text()
            assert "from src.app.features.tasks import router" in main_py
