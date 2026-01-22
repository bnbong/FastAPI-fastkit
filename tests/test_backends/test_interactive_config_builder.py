# --------------------------------------------------------------------------
# Test cases for backend/interactive/config_builder.py
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from unittest.mock import MagicMock, call, patch

import pytest

from fastapi_fastkit.backend.interactive.config_builder import InteractiveConfigBuilder
from fastapi_fastkit.core.settings import FastkitConfig


class TestInteractiveConfigBuilderInitialization:
    """Test cases for InteractiveConfigBuilder initialization."""

    def test_initialization_with_settings(self) -> None:
        """Test InteractiveConfigBuilder initialization."""
        # given
        settings = FastkitConfig()

        # when
        builder = InteractiveConfigBuilder(settings)

        # then
        assert builder.settings is not None
        assert isinstance(builder.config, dict)
        assert len(builder.config) == 0

    def test_initialization_config_empty(self) -> None:
        """Test that config starts empty."""
        # given
        settings = FastkitConfig()

        # when
        builder = InteractiveConfigBuilder(settings)

        # then
        assert builder.config == {}


class TestCollectAllDependencies:
    """Test cases for _collect_all_dependencies method."""

    def test_collect_dependencies_minimal(self) -> None:
        """Test dependency collection with minimal config."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)
        builder.config = {
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
        dependencies = builder._collect_all_dependencies()

        # then
        assert "fastapi" in dependencies
        assert "uvicorn" in dependencies
        assert "pydantic" in dependencies
        assert "pydantic-settings" in dependencies

    def test_collect_dependencies_with_database(self) -> None:
        """Test dependency collection includes database packages."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)
        builder.config = {
            "database": {"type": "PostgreSQL", "packages": ["sqlalchemy", "asyncpg"]},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": [],
        }

        # when
        dependencies = builder._collect_all_dependencies()

        # then
        assert "sqlalchemy" in dependencies
        assert "asyncpg" in dependencies

    def test_collect_dependencies_with_authentication(self) -> None:
        """Test dependency collection includes authentication packages."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)
        builder.config = {
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
        dependencies = builder._collect_all_dependencies()

        # then
        assert "python-jose[cryptography]" in dependencies
        assert "passlib[bcrypt]" in dependencies

    def test_collect_dependencies_deduplication(self) -> None:
        """Test that dependencies are deduplicated."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)
        builder.config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": ["fastapi", "uvicorn"],  # Duplicates base deps
        }

        # when
        dependencies = builder._collect_all_dependencies()

        # then
        # Should only appear once
        assert dependencies.count("fastapi") == 1
        assert dependencies.count("uvicorn") == 1

    def test_collect_dependencies_sorted(self) -> None:
        """Test that dependencies are sorted alphabetically."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)
        builder.config = {
            "database": {"type": "PostgreSQL", "packages": ["sqlalchemy", "asyncpg"]},
            "authentication": "JWT",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "custom_packages": ["zebra", "aardvark"],
        }

        # when
        dependencies = builder._collect_all_dependencies()

        # then
        sorted_deps = sorted(dependencies)
        assert dependencies == sorted_deps

    def test_collect_dependencies_with_utilities(self) -> None:
        """Test dependency collection with utilities."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)
        builder.config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": ["Rate-Limiting"],
            "custom_packages": [],
        }

        # when
        dependencies = builder._collect_all_dependencies()

        # then
        assert "slowapi" in dependencies


class TestBuildFinalConfig:
    """Test cases for _build_final_config method."""

    def test_build_final_config_adds_dependencies(self) -> None:
        """Test that build_final_config adds all_dependencies to config."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)
        builder.config = {
            "project_name": "test-project",
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
        final_config = builder._build_final_config()

        # then
        assert "all_dependencies" in final_config
        assert isinstance(final_config["all_dependencies"], list)
        assert len(final_config["all_dependencies"]) > 0

    def test_build_final_config_preserves_existing_config(self) -> None:
        """Test that build_final_config preserves existing configuration."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)
        builder.config = {
            "project_name": "my-project",
            "author": "Test Author",
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
        final_config = builder._build_final_config()

        # then
        assert final_config["project_name"] == "my-project"
        assert final_config["author"] == "Test Author"


class TestRunInteractiveFlow:
    """Test cases for run_interactive_flow method with mocked prompts."""

    @patch("fastapi_fastkit.backend.interactive.config_builder.confirm_selections")
    @patch(
        "fastapi_fastkit.backend.interactive.config_builder.validate_feature_compatibility"
    )
    @patch(
        "fastapi_fastkit.backend.interactive.config_builder.prompt_additional_features"
    )
    @patch(
        "fastapi_fastkit.backend.interactive.config_builder.prompt_template_selection"
    )
    @patch("fastapi_fastkit.backend.interactive.config_builder.prompt_basic_info")
    def test_run_interactive_flow_full_journey(
        self,
        mock_basic_info,
        mock_template,
        mock_features,
        mock_validate,
        mock_confirm,
    ) -> None:
        """Test complete interactive flow from start to finish."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)

        mock_basic_info.return_value = {
            "project_name": "test-project",
            "author": "Test Author",
            "author_email": "test@example.com",
            "description": "Test description",
        }
        mock_template.return_value = None  # Empty template
        mock_features.return_value = {
            "database": {"type": "PostgreSQL", "packages": ["sqlalchemy", "asyncpg"]},
            "authentication": "JWT",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "Basic",
            "utilities": [],
            "deployment": [],
            "package_manager": "uv",
            "custom_packages": [],
        }
        mock_validate.return_value = (True, None)
        mock_confirm.return_value = True

        # when
        config = builder.run_interactive_flow()

        # then
        assert config is not None
        assert config["project_name"] == "test-project"
        assert config["author"] == "Test Author"
        assert config["authentication"] == "JWT"
        assert "all_dependencies" in config

    @patch("fastapi_fastkit.backend.interactive.config_builder.confirm_selections")
    @patch(
        "fastapi_fastkit.backend.interactive.config_builder.validate_feature_compatibility"
    )
    @patch(
        "fastapi_fastkit.backend.interactive.config_builder.prompt_additional_features"
    )
    @patch(
        "fastapi_fastkit.backend.interactive.config_builder.prompt_template_selection"
    )
    @patch("fastapi_fastkit.backend.interactive.config_builder.prompt_basic_info")
    def test_run_interactive_flow_user_cancels(
        self,
        mock_basic_info,
        mock_template,
        mock_features,
        mock_validate,
        mock_confirm,
    ) -> None:
        """Test interactive flow when user cancels."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)

        mock_basic_info.return_value = {
            "project_name": "test-project",
            "author": "Test Author",
            "author_email": "test@example.com",
            "description": "Test",
        }
        mock_template.return_value = None
        mock_features.return_value = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "deployment": [],
            "package_manager": "uv",
            "custom_packages": [],
        }
        mock_validate.return_value = (True, None)
        mock_confirm.return_value = False  # User cancels

        # when
        config = builder.run_interactive_flow()

        # then
        assert config == {}

    @patch("fastapi_fastkit.backend.interactive.config_builder.confirm_selections")
    @patch(
        "fastapi_fastkit.backend.interactive.config_builder.validate_feature_compatibility"
    )
    @patch(
        "fastapi_fastkit.backend.interactive.config_builder.prompt_additional_features"
    )
    @patch(
        "fastapi_fastkit.backend.interactive.config_builder.prompt_template_selection"
    )
    @patch("fastapi_fastkit.backend.interactive.config_builder.prompt_basic_info")
    def test_run_interactive_flow_with_warnings(
        self,
        mock_basic_info,
        mock_template,
        mock_features,
        mock_validate,
        mock_confirm,
    ) -> None:
        """Test interactive flow with feature compatibility warnings."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)

        mock_basic_info.return_value = {
            "project_name": "test-project",
            "author": "Test",
            "author_email": "test@example.com",
            "description": "Test",
        }
        mock_template.return_value = None
        mock_features.return_value = {
            "database": {"type": "None"},
            "authentication": "FastAPI-Users",  # Requires database
            "async_tasks": "None",
            "caching": "None",
            "monitoring": "None",
            "testing": "None",
            "utilities": [],
            "deployment": [],
            "package_manager": "uv",
            "custom_packages": [],
        }
        mock_validate.return_value = (True, "FastAPI-Users requires a database")
        mock_confirm.return_value = True

        # when
        config = builder.run_interactive_flow()

        # then
        assert config is not None
        assert config["authentication"] == "FastAPI-Users"


class TestGetConfig:
    """Test cases for get_config method."""

    def test_get_config_returns_current_config(self) -> None:
        """Test that get_config returns current configuration."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)
        builder.config = {
            "project_name": "test",
            "author": "Test Author",
        }

        # when
        config = builder.get_config()

        # then
        assert config["project_name"] == "test"
        assert config["author"] == "Test Author"

    def test_get_config_empty_initially(self) -> None:
        """Test that get_config returns empty dict initially."""
        # given
        settings = FastkitConfig()
        builder = InteractiveConfigBuilder(settings)

        # when
        config = builder.get_config()

        # then
        assert config == {}
