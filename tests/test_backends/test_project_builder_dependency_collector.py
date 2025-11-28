# --------------------------------------------------------------------------
# Test cases for backend/project_builder/dependency_collector.py
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import pytest

from fastapi_fastkit.backend.project_builder.dependency_collector import (
    DependencyCollector,
)
from fastapi_fastkit.core.settings import FastkitConfig


class TestDependencyCollectorInitialization:
    """Test cases for DependencyCollector initialization."""

    def test_initialization_with_settings(self) -> None:
        """Test DependencyCollector initialization with settings."""
        # given
        settings = FastkitConfig()

        # when
        collector = DependencyCollector(settings)

        # then
        assert collector.settings is not None
        assert len(collector.dependencies) == 0

    def test_initialization_dependencies_empty(self) -> None:
        """Test that dependencies start empty."""
        # given
        settings = FastkitConfig()

        # when
        collector = DependencyCollector(settings)

        # then
        assert isinstance(collector.dependencies, set)
        assert len(collector.dependencies) == 0


class TestCollectFromConfig:
    """Test cases for collect_from_config method."""

    def test_collect_minimal_config(self) -> None:
        """Test dependency collection with minimal config."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        assert len(dependencies) > 0
        assert "fastapi" in dependencies
        assert "uvicorn" in dependencies
        assert "pydantic" in dependencies
        assert "pydantic-settings" in dependencies

    def test_collect_with_postgresql(self) -> None:
        """Test dependency collection with PostgreSQL."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "PostgreSQL"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        assert "sqlalchemy" in dependencies
        assert "asyncpg" in dependencies
        assert "fastapi" in dependencies

    def test_collect_with_mongodb(self) -> None:
        """Test dependency collection with MongoDB."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "MongoDB"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        assert "motor" in dependencies
        assert "fastapi" in dependencies

    def test_collect_with_jwt_authentication(self) -> None:
        """Test dependency collection with JWT authentication."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "None"},
            "authentication": "JWT",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        assert "python-jose[cryptography]" in dependencies
        assert "passlib[bcrypt]" in dependencies

    def test_collect_with_celery(self) -> None:
        """Test dependency collection with Celery."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "Celery",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        # Celery comes with redis extra
        assert any("celery" in dep for dep in dependencies)
        assert any("redis" in dep for dep in dependencies)

    def test_collect_with_redis_caching(self) -> None:
        """Test dependency collection with Redis caching."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "Redis",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        # Redis may come with hiredis extra
        assert any("redis" in dep for dep in dependencies)

    def test_collect_with_prometheus_monitoring(self) -> None:
        """Test dependency collection with Prometheus monitoring."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "Prometheus",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        assert "prometheus-fastapi-instrumentator" in dependencies

    def test_collect_with_pytest_testing(self) -> None:
        """Test dependency collection with pytest testing."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "Basic",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        assert "pytest" in dependencies
        assert "pytest-asyncio" in dependencies
        assert "httpx" in dependencies

    def test_collect_with_custom_packages(self) -> None:
        """Test dependency collection with custom packages."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": ["requests", "aiohttp"],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        assert "requests" in dependencies
        assert "aiohttp" in dependencies

    def test_collect_full_stack_config(self) -> None:
        """Test dependency collection with full stack configuration."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "PostgreSQL"},
            "authentication": "JWT",
            "async_tasks": "Celery",
            "caching": "Redis",
            "monitoring": "Prometheus",
            "testing": "Coverage",
            "utilities": ["Rate-Limiting"],
            "custom_packages": ["requests"],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        # Base dependencies
        assert "fastapi" in dependencies
        assert "uvicorn" in dependencies
        # Database
        assert "sqlalchemy" in dependencies
        assert "asyncpg" in dependencies
        # Authentication
        assert "python-jose[cryptography]" in dependencies
        # Tasks
        assert any("celery" in dep for dep in dependencies)
        assert any("redis" in dep for dep in dependencies)
        # Monitoring
        assert "prometheus-fastapi-instrumentator" in dependencies
        # Testing
        assert "pytest" in dependencies
        assert "pytest-cov" in dependencies
        # Custom
        assert "requests" in dependencies


class TestDependencyDeduplication:
    """Test cases for dependency deduplication logic."""

    def test_deduplication_with_shared_redis(self) -> None:
        """Test that Redis is not duplicated when used for both cache and tasks."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "Celery",  # Includes redis
            "caching": "Redis",  # Also redis
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        redis_count = dependencies.count("redis")
        assert redis_count == 1, "Redis should appear only once"

    def test_deduplication_with_duplicate_custom_packages(self) -> None:
        """Test deduplication of duplicate custom packages."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": ["requests", "requests", "aiohttp"],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        requests_count = dependencies.count("requests")
        assert requests_count == 1, "requests should appear only once"

    def test_dependencies_are_sorted(self) -> None:
        """Test that returned dependencies are sorted."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config = {
            "database": {"type": "PostgreSQL"},
            "authentication": "JWT",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": ["zebra", "aardvark"],
        }

        # when
        dependencies = collector.collect_from_config(config)

        # then
        sorted_deps = sorted(dependencies)
        assert dependencies == sorted_deps


class TestIndividualDependencyMethods:
    """Test cases for individual add_*_dependencies methods."""

    def test_add_base_dependencies(self) -> None:
        """Test add_base_dependencies method."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)

        # when
        collector.add_base_dependencies()

        # then
        assert "fastapi" in collector.dependencies
        assert "uvicorn" in collector.dependencies
        assert "pydantic" in collector.dependencies
        assert "pydantic-settings" in collector.dependencies

    def test_add_database_dependencies_postgresql(self) -> None:
        """Test add_database_dependencies for PostgreSQL."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)

        # when
        collector.add_database_dependencies("PostgreSQL")

        # then
        assert "sqlalchemy" in collector.dependencies
        assert "asyncpg" in collector.dependencies

    def test_add_database_dependencies_mysql(self) -> None:
        """Test add_database_dependencies for MySQL."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)

        # when
        collector.add_database_dependencies("MySQL")

        # then
        assert "sqlalchemy" in collector.dependencies
        assert "aiomysql" in collector.dependencies

    def test_add_authentication_dependencies_oauth2(self) -> None:
        """Test add_authentication_dependencies for OAuth2."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)

        # when
        collector.add_authentication_dependencies("OAuth2")

        # then
        assert "authlib" in collector.dependencies

    def test_add_utility_dependencies_rate_limiting(self) -> None:
        """Test add_utility_dependencies for Rate-Limiting."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)

        # when
        collector.add_utility_dependencies("Rate-Limiting")

        # then
        assert "slowapi" in collector.dependencies


class TestGetFinalDependencies:
    """Test cases for get_final_dependencies method."""

    def test_get_final_dependencies_returns_list(self) -> None:
        """Test that get_final_dependencies returns a list."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        collector.add_base_dependencies()

        # when
        result = collector.get_final_dependencies()

        # then
        assert isinstance(result, list)

    def test_get_dependency_count(self) -> None:
        """Test get_dependency_count method."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        collector.add_base_dependencies()

        # when
        count = collector.get_dependency_count()

        # then
        assert count == 4  # fastapi, uvicorn, pydantic, pydantic-settings

    def test_collect_resets_dependencies(self) -> None:
        """Test that collect_from_config resets dependencies each time."""
        # given
        settings = FastkitConfig()
        collector = DependencyCollector(settings)
        config1 = {
            "database": {"type": "PostgreSQL"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }
        config2 = {
            "database": {"type": "MongoDB"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        deps1 = collector.collect_from_config(config1)
        deps2 = collector.collect_from_config(config2)

        # then
        # Should have MongoDB dependencies, not PostgreSQL
        assert "motor" in deps2
        assert "asyncpg" not in deps2
        # But PostgreSQL was in first collection
        assert "asyncpg" in deps1
