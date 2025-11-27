# --------------------------------------------------------------------------
# Test cases for backend/interactive/prompts.py
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from unittest.mock import MagicMock, patch

import pytest

from fastapi_fastkit.backend.interactive import prompts
from fastapi_fastkit.core.settings import FastkitConfig


class TestPromptBasicInfo:
    """Test cases for prompt_basic_info function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    @patch("fastapi_fastkit.backend.interactive.prompts.validate_project_name")
    @patch("fastapi_fastkit.backend.interactive.prompts.validate_email_format")
    def test_prompt_basic_info_valid_inputs(
        self, mock_email_val, mock_name_val, mock_prompt
    ) -> None:
        """Test prompt_basic_info with valid inputs."""
        # given
        mock_prompt.side_effect = [
            "test-project",
            "Test Author",
            "test@example.com",
            "A test description",
        ]
        mock_name_val.return_value = (True, None)
        mock_email_val.return_value = True

        # when
        result = prompts.prompt_basic_info()

        # then
        assert result["project_name"] == "test-project"
        assert result["author"] == "Test Author"
        assert result["author_email"] == "test@example.com"
        assert result["description"] == "A test description"


class TestPromptTemplateSelection:
    """Test cases for prompt_template_selection function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    @patch("fastapi_fastkit.backend.interactive.prompts.render_selection_table")
    def test_prompt_template_selection_empty_project(
        self, mock_render, mock_prompt
    ) -> None:
        """Test selecting empty project template."""
        # given
        settings = FastkitConfig()
        mock_prompt.return_value = 1  # First option (Empty Project)

        # when
        result = prompts.prompt_template_selection(settings)

        # then
        # Empty project returns None
        assert result is None or isinstance(result, str)


class TestPromptDatabaseSelection:
    """Test cases for prompt_database_selection function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    def test_prompt_database_selection_postgresql(self, mock_prompt) -> None:
        """Test selecting PostgreSQL database."""
        # given
        settings = FastkitConfig()
        # Assuming PostgreSQL is first in catalog
        mock_prompt.return_value = 1

        # when
        result = prompts.prompt_database_selection(settings)

        # then
        assert "type" in result
        assert "packages" in result


class TestPromptAuthenticationSelection:
    """Test cases for prompt_authentication_selection function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    def test_prompt_authentication_selection(self, mock_prompt) -> None:
        """Test selecting authentication method."""
        # given
        settings = FastkitConfig()
        mock_prompt.return_value = 1  # First option

        # when
        result = prompts.prompt_authentication_selection(settings)

        # then
        assert isinstance(result, str)


class TestPromptPackageManagerSelection:
    """Test cases for prompt_package_manager_selection function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    def test_prompt_package_manager_selection(self, mock_prompt) -> None:
        """Test selecting package manager."""
        # given
        settings = FastkitConfig()
        mock_prompt.return_value = 1

        # when
        result = prompts.prompt_package_manager_selection(settings)

        # then
        assert isinstance(result, str)
        assert result in ["pip", "uv", "pdm", "poetry"]


class TestPromptCustomPackages:
    """Test cases for prompt_custom_packages function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.console.input")
    def test_prompt_custom_packages_with_input(self, mock_input) -> None:
        """Test entering custom packages."""
        # given
        mock_input.return_value = "requests, aiohttp, httpx"

        # when
        result = prompts.prompt_custom_packages()

        # then
        assert isinstance(result, list)
        assert "requests" in result
        assert "aiohttp" in result
        assert "httpx" in result

    @patch("fastapi_fastkit.backend.interactive.prompts.console.input")
    def test_prompt_custom_packages_empty(self, mock_input) -> None:
        """Test skipping custom packages."""
        # given
        mock_input.return_value = ""

        # when
        result = prompts.prompt_custom_packages()

        # then
        assert result == []


class TestPromptDeploymentOptions:
    """Test cases for prompt_deployment_options function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    def test_prompt_deployment_options_none(self, mock_prompt) -> None:
        """Test selecting no deployment options."""
        # given
        mock_prompt.return_value = 3  # "None" option

        # when
        result = prompts.prompt_deployment_options()

        # then
        assert result == []

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    def test_prompt_deployment_options_docker(self, mock_prompt) -> None:
        """Test selecting Docker deployment."""
        # given
        mock_prompt.return_value = 1  # "Docker" option

        # when
        result = prompts.prompt_deployment_options()

        # then
        assert "Docker" in result

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    def test_prompt_deployment_options_docker_compose(self, mock_prompt) -> None:
        """Test selecting docker-compose deployment."""
        # given
        mock_prompt.return_value = 2  # "docker-compose" option

        # when
        result = prompts.prompt_deployment_options()

        # then
        assert "Docker" in result
        assert "docker-compose" in result
