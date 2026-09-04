# --------------------------------------------------------------------------
# Test cases for backend/interactive/prompts.py
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from unittest.mock import patch

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


class TestPromptArchitecturePreset:
    """Test cases for prompt_architecture_preset function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    @patch("fastapi_fastkit.backend.interactive.prompts.render_selection_table")
    def test_prompt_architecture_preset_default_is_domain_starter(
        self, mock_render, mock_prompt
    ) -> None:
        """Default selection (Enter on the prompt) yields the documented default."""
        # given
        settings = FastkitConfig()
        # Returning the default index simulates the user pressing Enter.
        preset_ids = list(settings.ARCHITECTURE_PRESETS.keys())
        default_idx = preset_ids.index(settings.DEFAULT_ARCHITECTURE_PRESET) + 1
        mock_prompt.return_value = default_idx

        # when
        result = prompts.prompt_architecture_preset(settings)

        # then
        assert result == settings.DEFAULT_ARCHITECTURE_PRESET == "domain-starter"
        # The settings catalog and the prompt's offered options must agree.
        mock_render.assert_called_once()
        rendered_options = mock_render.call_args.args[1]
        assert list(rendered_options.keys()) == preset_ids

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    @patch("fastapi_fastkit.backend.interactive.prompts.render_selection_table")
    def test_prompt_architecture_preset_explicit_minimal(
        self, mock_render, mock_prompt
    ) -> None:
        """Selecting the first option returns ``minimal``."""
        # given
        settings = FastkitConfig()
        mock_prompt.return_value = 1

        # when
        result = prompts.prompt_architecture_preset(settings)

        # then
        assert result == "minimal"

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    @patch("fastapi_fastkit.backend.interactive.prompts.render_selection_table")
    def test_prompt_architecture_preset_offers_all_required_ids(
        self, mock_render, mock_prompt
    ) -> None:
        """All four preset ids required by issue #44 must be offered."""
        # given
        settings = FastkitConfig()
        mock_prompt.return_value = 1

        # when
        prompts.prompt_architecture_preset(settings)

        # then
        offered = set(mock_render.call_args.args[1].keys())
        assert offered == {
            "minimal",
            "single-module",
            "classic-layered",
            "domain-starter",
        }

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    @patch("fastapi_fastkit.backend.interactive.prompts.render_selection_table")
    def test_prompt_architecture_preset_marks_recommended_default(
        self, mock_render, mock_prompt
    ) -> None:
        """Default preset's row must be visibly annotated as recommended."""
        # given
        settings = FastkitConfig()
        mock_prompt.return_value = 1

        # when
        prompts.prompt_architecture_preset(settings)

        # then — only the default's display description carries the marker.
        rendered_options = mock_render.call_args.args[1]
        default_id = settings.DEFAULT_ARCHITECTURE_PRESET
        assert "recommended default" in rendered_options[default_id].lower()
        for preset_id, description in rendered_options.items():
            if preset_id == default_id:
                continue
            assert "recommended default" not in description.lower()


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


class TestPromptLoggingSelection:
    """Test cases for prompt_logging_selection function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    def test_selects_structured_logging(self, mock_prompt) -> None:
        """Test picking the structured (JSON) logging option."""
        # given
        settings = FastkitConfig()
        mock_prompt.return_value = 1

        # when
        result = prompts.prompt_logging_selection(settings)

        # then
        assert result == "structured"

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    def test_defaults_to_none(self, mock_prompt) -> None:
        """Test that the prompt defaults to the last (None) option."""
        # given
        settings = FastkitConfig()
        mock_prompt.return_value = 2

        # when
        result = prompts.prompt_logging_selection(settings)

        # then
        assert result == "None"
        assert mock_prompt.call_args.kwargs["default"] == 2


class TestPromptMigrationsSelection:
    """Test cases for prompt_migrations_selection function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    def test_recommends_alembic_for_sql_databases(self, mock_prompt) -> None:
        """A relational database pre-selects Alembic as the default."""
        # given
        settings = FastkitConfig()
        mock_prompt.return_value = 1

        # when
        result = prompts.prompt_migrations_selection(settings, "PostgreSQL")

        # then
        assert result == "Alembic"
        assert mock_prompt.call_args.kwargs["default"] == 1

    @patch("fastapi_fastkit.backend.interactive.prompts.click.prompt")
    def test_defaults_to_none_without_a_sql_database(self, mock_prompt) -> None:
        """Alembic has nothing to migrate on MongoDB, so it is not default."""
        # given
        settings = FastkitConfig()
        mock_prompt.return_value = 2

        # when
        result = prompts.prompt_migrations_selection(settings, "MongoDB")

        # then
        assert result == "None"
        assert mock_prompt.call_args.kwargs["default"] == 2


class TestPromptToolingSelection:
    """Test cases for prompt_tooling_selection function."""

    @patch("fastapi_fastkit.backend.interactive.prompts.console")
    def test_parses_a_comma_separated_multi_select(self, mock_console) -> None:
        """Test selecting several tooling options at once."""
        # given
        settings = FastkitConfig()
        mock_console.input.return_value = "1,5"

        # when
        result = prompts.prompt_tooling_selection(settings)

        # then
        assert result == ["ruff", "makefile"]

    @patch("fastapi_fastkit.backend.interactive.prompts.console")
    def test_empty_input_skips_tooling(self, mock_console) -> None:
        """Test that pressing Enter selects nothing."""
        # given
        settings = FastkitConfig()
        mock_console.input.return_value = ""

        # when
        result = prompts.prompt_tooling_selection(settings)

        # then
        assert result == []

    @patch("fastapi_fastkit.backend.interactive.prompts.console")
    def test_invalid_input_is_ignored(self, mock_console) -> None:
        """Test that a non-numeric answer degrades to no selection."""
        # given
        settings = FastkitConfig()
        mock_console.input.return_value = "ruff, makefile"

        # when
        result = prompts.prompt_tooling_selection(settings)

        # then
        assert result == []

    @patch("fastapi_fastkit.backend.interactive.prompts.console")
    def test_never_offers_the_none_sentinel(self, mock_console) -> None:
        """``None`` is the absence of a selection, not a selectable option."""
        # given
        settings = FastkitConfig()
        mock_console.input.return_value = "1,2,3,4,5,6"

        # when
        result = prompts.prompt_tooling_selection(settings)

        # then
        assert "None" not in result
        assert len(result) == 5


class TestPromptAdditionalFeaturesCoversEveryAxis:
    """The aggregate flow must ask about every catalog axis."""

    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_custom_packages")
    @patch(
        "fastapi_fastkit.backend.interactive.prompts.prompt_package_manager_selection"
    )
    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_deployment_options")
    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_tooling_selection")
    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_utilities_selection")
    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_migrations_selection")
    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_testing_selection")
    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_logging_selection")
    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_monitoring_selection")
    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_caching_selection")
    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_async_tasks_selection")
    @patch(
        "fastapi_fastkit.backend.interactive.prompts.prompt_authentication_selection"
    )
    @patch("fastapi_fastkit.backend.interactive.prompts.prompt_database_selection")
    def test_collects_every_axis(
        self,
        mock_database,
        mock_auth,
        mock_tasks,
        mock_caching,
        mock_monitoring,
        mock_logging,
        mock_testing,
        mock_migrations,
        mock_utilities,
        mock_tooling,
        mock_deployment,
        mock_package_manager,
        mock_custom,
    ) -> None:
        """Every axis the generator reads must be present in the result."""
        # given
        settings = FastkitConfig()
        mock_database.return_value = {"type": "PostgreSQL", "packages": []}
        mock_auth.return_value = "JWT"
        mock_tasks.return_value = "Celery"
        mock_caching.return_value = "Redis"
        mock_monitoring.return_value = "Prometheus"
        mock_logging.return_value = "structured"
        mock_testing.return_value = "Advanced"
        mock_migrations.return_value = "Alembic"
        mock_utilities.return_value = ["CORS"]
        mock_tooling.return_value = ["ruff"]
        mock_deployment.return_value = ["Docker"]
        mock_package_manager.return_value = "uv"
        mock_custom.return_value = []

        # when
        features = prompts.prompt_additional_features(settings)

        # then
        assert features["logging"] == "structured"
        assert features["migrations"] == "Alembic"
        assert features["tooling"] == ["ruff"]
        # The migrations prompt needs the database choice to pick its default.
        mock_migrations.assert_called_once_with(settings, "PostgreSQL")
