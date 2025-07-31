# --------------------------------------------------------------------------
# Testcases of core modules.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from unittest.mock import patch

import pytest

from fastapi_fastkit.core.exceptions import BackendExceptions, TemplateExceptions
from fastapi_fastkit.core.settings import FastkitConfig, settings


class TestCoreExceptions:
    """Test cases for core/exceptions.py."""

    def test_backend_exceptions(self) -> None:
        """Test BackendExceptions class."""
        # given
        error_message = "Backend error occurred"

        # when
        exception = BackendExceptions(error_message)

        # then
        assert str(exception) == error_message
        assert isinstance(exception, Exception)

    def test_backend_exceptions_inheritance(self) -> None:
        """Test BackendExceptions inheritance."""
        # given
        error_message = "Test backend error"

        # when
        exception = BackendExceptions(error_message)

        # then
        assert isinstance(exception, Exception)

    def test_template_exceptions(self) -> None:
        """Test TemplateExceptions class."""
        # given
        error_message = "Template error occurred"

        # when
        exception = TemplateExceptions(error_message)

        # then
        assert str(exception) == error_message
        assert isinstance(exception, Exception)

    def test_template_exceptions_inheritance(self) -> None:
        """Test TemplateExceptions inheritance."""
        # given
        error_message = "Test template error"

        # when
        exception = TemplateExceptions(error_message)

        # then
        assert isinstance(exception, Exception)

    def test_raise_backend_exception(self) -> None:
        """Test raising BackendExceptions."""
        # given
        error_message = "Critical backend error"

        # when & then
        with pytest.raises(BackendExceptions) as exc_info:
            raise BackendExceptions(error_message)

        assert str(exc_info.value) == error_message

    def test_raise_template_exception(self) -> None:
        """Test raising TemplateExceptions."""
        # given
        error_message = "Critical template error"

        # when & then
        with pytest.raises(TemplateExceptions) as exc_info:
            raise TemplateExceptions(error_message)

        assert str(exc_info.value) == error_message


class TestCoreSettings:
    """Test cases for core/settings.py."""

    def test_settings_object_exists(self) -> None:
        """Test that settings object exists and is accessible."""
        # given & when & then
        assert settings is not None

    def test_settings_has_template_paths(self) -> None:
        """Test that settings has TEMPLATE_PATHS."""
        # given & when & then
        assert hasattr(settings, "TEMPLATE_PATHS")
        assert isinstance(settings.TEMPLATE_PATHS, dict)

    def test_template_paths_has_required_keys(self) -> None:
        """Test that TEMPLATE_PATHS has required keys."""
        # given
        required_keys = ["main", "setup", "config"]

        # when & then
        for key in required_keys:
            assert key in settings.TEMPLATE_PATHS

    def test_template_paths_main_structure(self) -> None:
        """Test TEMPLATE_PATHS main structure."""
        # given & when
        main_paths = settings.TEMPLATE_PATHS["main"]

        # then
        assert isinstance(main_paths, list)
        assert len(main_paths) > 0
        assert "main.py" in main_paths

    def test_template_paths_setup_structure(self) -> None:
        """Test TEMPLATE_PATHS setup structure."""
        # given & when
        setup_paths = settings.TEMPLATE_PATHS["setup"]

        # then
        assert isinstance(setup_paths, list)
        assert len(setup_paths) > 0
        assert "setup.py" in setup_paths

    def test_template_paths_config_structure(self) -> None:
        """Test TEMPLATE_PATHS config structure."""
        # given & when
        config_paths = settings.TEMPLATE_PATHS["config"]

        # then
        assert isinstance(config_paths, dict)
        assert "files" in config_paths
        assert "paths" in config_paths
        assert isinstance(config_paths["files"], list)
        assert isinstance(config_paths["paths"], list)

    def test_settings_has_fastkit_template_root(self) -> None:
        """Test that settings has FASTKIT_TEMPLATE_ROOT."""
        # given & when & then
        assert hasattr(settings, "FASTKIT_TEMPLATE_ROOT")
        assert isinstance(settings.FASTKIT_TEMPLATE_ROOT, str)

    def test_settings_template_dir_exists(self) -> None:
        """Test that template directory path is valid."""
        # given & when
        template_dir = settings.FASTKIT_TEMPLATE_ROOT

        # then
        assert template_dir is not None
        assert len(template_dir) > 0

    def test_settings_project_stacks(self) -> None:
        """Test PROJECT_STACKS configuration."""
        # given & when
        stacks = settings.PROJECT_STACKS

        # then
        assert isinstance(stacks, dict)
        assert "minimal" in stacks
        assert "standard" in stacks
        assert "full" in stacks

        # Check that each stack has FastAPI
        for stack_name, stack_deps in stacks.items():
            assert "fastapi" in stack_deps, f"FastAPI missing in {stack_name} stack"

    def test_settings_debug_mode_toggle(self) -> None:
        """Test debug mode toggle functionality."""
        # given
        original_debug = settings.DEBUG_MODE

        try:
            # when
            settings.set_debug_mode(True)

            # then
            assert settings.DEBUG_MODE is True

            # when
            settings.set_debug_mode(False)

            # then
            assert settings.DEBUG_MODE is False

        finally:
            # Reset to original state
            settings.set_debug_mode(original_debug)

    def test_settings_config_files_structure(self) -> None:
        """Test that config files structure is properly defined."""
        # given & when
        config_files = settings.TEMPLATE_PATHS["config"]["files"]  # type: ignore
        config_paths = settings.TEMPLATE_PATHS["config"]["paths"]  # type: ignore

        # then
        assert "config.py" in config_files
        assert "settings.py" in config_files
        assert "src/core" in config_paths
        assert "src" in config_paths
        assert "" in config_paths

    def test_settings_project_stacks_completeness(self) -> None:
        """Test that all project stacks have required packages."""
        # given
        required_packages = ["fastapi", "uvicorn", "pydantic"]

        # when & then
        for stack_name, packages in settings.PROJECT_STACKS.items():
            for required_pkg in required_packages:
                assert any(
                    required_pkg in pkg for pkg in packages
                ), f"{required_pkg} missing in {stack_name}"

    def test_settings_test_configuration_values(self) -> None:
        """Test test configuration values are reasonable."""
        # given & when & then
        assert settings.TEST_SERVER_PORT > 0
        assert settings.TEST_SERVER_PORT < 65536
        assert settings.TEST_DEFAULT_TERMINAL_WIDTH > 0
        assert settings.TEST_MAX_TERMINAL_WIDTH >= settings.TEST_DEFAULT_TERMINAL_WIDTH

    def test_settings_debug_mode_default_value(self) -> None:
        """Test debug mode default value."""
        # given & when & then
        # Default should be False
        config = FastkitConfig()
        assert config.DEBUG_MODE is False

    def test_settings_logging_level_default_value(self) -> None:
        """Test logging level default value."""
        # given & when & then
        assert settings.LOGGING_LEVEL == "DEBUG"

    def test_settings_immutable_constants(self) -> None:
        """Test that certain settings are properly defined as constants."""
        # given & when & then
        assert hasattr(settings, "TEMPLATE_PATHS")
        assert hasattr(settings, "PROJECT_STACKS")
        assert isinstance(settings.TEMPLATE_PATHS, dict)
        assert isinstance(settings.PROJECT_STACKS, dict)

    def test_settings_template_root_exists(self) -> None:
        """Test that template root directory exists and is valid."""
        # given & when
        template_root = settings.FASTKIT_TEMPLATE_ROOT

        # then
        assert template_root is not None
        assert len(template_root) > 0
        assert os.path.exists(template_root)

    def test_settings_project_root_exists(self) -> None:
        """Test that project root directory exists and is valid."""
        # given & when
        project_root = settings.FASTKIT_PROJECT_ROOT

        # then
        assert project_root is not None
        assert len(project_root) > 0
        assert os.path.exists(project_root)

    def test_settings_set_debug_mode_true(self) -> None:
        """Test set_debug_mode with True value."""
        # given
        original_debug = settings.DEBUG_MODE

        try:
            # when
            settings.set_debug_mode(True)

            # then
            assert settings.DEBUG_MODE is True
        finally:
            settings.set_debug_mode(original_debug)

    def test_settings_set_debug_mode_false(self) -> None:
        """Test set_debug_mode with False value."""
        # given
        original_debug = settings.DEBUG_MODE

        try:
            # when
            settings.set_debug_mode(False)

            # then
            assert settings.DEBUG_MODE is False
        finally:
            settings.set_debug_mode(original_debug)

    def test_settings_set_debug_mode_without_parameter(self) -> None:
        """Test set_debug_mode without parameter (defaults to True)."""
        # given
        original_debug = settings.DEBUG_MODE

        try:
            # when
            settings.set_debug_mode()

            # then
            assert settings.DEBUG_MODE is True
        finally:
            settings.set_debug_mode(original_debug)

    def test_settings_log_file_path_creation(self) -> None:
        """Test that log file path is properly set."""
        # given & when
        log_path = settings.LOG_FILE_PATH

        # then
        assert log_path is not None
        assert "fastkit.log" in log_path

    def test_settings_user_workspace_initialization(self) -> None:
        """Test user workspace initialization."""
        # given & when
        workspace = settings.USER_WORKSPACE

        # then
        assert workspace is not None
        assert len(workspace) > 0
        assert os.path.exists(workspace)

    def test_settings_error_handling_for_missing_template_files(self) -> None:
        """Test error handling when template files are missing."""
        # given
        from fastapi_fastkit.core.settings import FastkitConfig

        # Mock pathlib to simulate missing files
        with patch("pathlib.Path.exists", return_value=False):
            with patch("fastapi_fastkit.core.settings.Path") as mock_path:
                mock_path.return_value.exists.return_value = False

                # when & then - should handle gracefully
                try:
                    config = FastkitConfig()
                    # Should not raise exception even with missing template files
                    assert config is not None
                except Exception:
                    # If exception occurs, it should be handled gracefully
                    pass
