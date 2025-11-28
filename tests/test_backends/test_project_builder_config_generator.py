# --------------------------------------------------------------------------
# Test cases for backend/project_builder/config_generator.py
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import pytest

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
        assert "@app.get('/', tags=['Health'])" in content
        assert "def root():" in content

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
        assert "from sqlalchemy.ext.asyncio import create_async_engine" in content
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
