"""
Test cases for core modules.
"""

import pytest

from fastapi_fastkit.core.exceptions import BackendExceptions, TemplateExceptions
from fastapi_fastkit.core.settings import settings


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
