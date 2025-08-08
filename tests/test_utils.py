# --------------------------------------------------------------------------
# Testcases of utils modules.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.utils.logging import setup_logging
from fastapi_fastkit.utils.main import (
    handle_exception,
    print_error,
    print_info,
    print_success,
    print_warning,
)


class TestUtilsMain:
    """Test cases for utils/main.py functions."""

    def test_handle_exception(self) -> None:
        """Test handle_exception function."""
        # given
        test_exception = ValueError("Test error")
        error_message = "Test error occurred"

        # when & then
        with patch("fastapi_fastkit.utils.main.print_error") as mock_print_error:
            handle_exception(test_exception, error_message)
            mock_print_error.assert_called_once()

    def test_print_functions(self) -> None:
        """Test print utility functions."""
        # given
        test_message = "Test message"

        # when & then
        with patch("fastapi_fastkit.console.print") as mock_console_print:
            print_error(test_message)
            print_info(test_message)
            print_success(test_message)
            print_warning(test_message)

            # Should have been called 4 times
            assert mock_console_print.call_count == 4

    def test_print_error_formatting(self) -> None:
        """Test print_error formatting."""
        # given
        error_message = "Critical error occurred"

        # when
        with patch("fastapi_fastkit.console.print") as mock_console_print:
            print_error(error_message)

            # then
            mock_console_print.assert_called_once()
            # Check that a Panel object was passed
            args, kwargs = mock_console_print.call_args
            assert len(args) > 0

    def test_print_success_formatting(self) -> None:
        """Test print_success formatting."""
        # given
        success_message = "Operation completed successfully"

        # when
        with patch("fastapi_fastkit.console.print") as mock_console_print:
            print_success(success_message)

            # then
            mock_console_print.assert_called_once()
            # Check that a Panel object was passed
            args, kwargs = mock_console_print.call_args
            assert len(args) > 0

    def test_print_warning_formatting(self) -> None:
        """Test print_warning formatting."""
        # given
        warning_message = "This is a warning"

        # when
        with patch("fastapi_fastkit.console.print") as mock_console_print:
            print_warning(warning_message)

            # then
            mock_console_print.assert_called_once()
            # Check that a Panel object was passed
            args, kwargs = mock_console_print.call_args
            assert len(args) > 0

    def test_print_info_formatting(self) -> None:
        """Test print_info formatting."""
        # given
        info_message = "Information message"

        # when
        with patch("fastapi_fastkit.console.print") as mock_console_print:
            print_info(info_message)

            # then
            mock_console_print.assert_called_once()
            # Check that a Panel object was passed
            args, kwargs = mock_console_print.call_args
            assert len(args) > 0


class TestUtilsLogging:
    """Test cases for utils/logging.py functions."""

    def test_setup_logging(self) -> None:
        """Test setup_logging function."""
        # given
        test_config = FastkitConfig()
        test_config.LOGGING_LEVEL = "INFO"

        # when
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            setup_logging(test_config)

            # then
            mock_get_logger.assert_called_once_with("fastapi-fastkit")
            mock_logger.setLevel.assert_called_once_with("INFO")

    def test_setup_logging_with_terminal_width(self) -> None:
        """Test setup_logging with custom terminal width."""
        # given
        test_config = FastkitConfig()
        test_config.LOGGING_LEVEL = "DEBUG"
        terminal_width = 120

        # when
        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            setup_logging(test_config, terminal_width)

            # then
            # Just check that logging was configured
            mock_get_logger.assert_called()
            mock_logger.setLevel.assert_called_once_with("DEBUG")

    def test_is_fastkit_project_function_with_setup_py(self, temp_dir: str) -> None:
        """Test is_fastkit_project function with setup.py containing fastkit metadata."""
        # given
        from fastapi_fastkit.utils.main import is_fastkit_project

        project_path = Path(temp_dir) / "fastkit-project"
        project_path.mkdir()
        setup_py = project_path / "setup.py"
        setup_py.write_text(
            """
from setuptools import setup
setup(
    name="test-project",
    description="Created with FastAPI-fastkit"
)
"""
        )

        # when & then
        assert is_fastkit_project(str(project_path)) is True

    def test_is_fastkit_project_function_invalid_path(self) -> None:
        """Test is_fastkit_project function with invalid path."""
        # given
        from fastapi_fastkit.utils.main import is_fastkit_project

        nonexistent_path = "/nonexistent/path"

        # when & then
        assert is_fastkit_project(nonexistent_path) is False

    def test_print_error_with_traceback(self) -> None:
        """Test print_error function with traceback enabled."""
        # given
        import io

        from rich.console import Console

        from fastapi_fastkit.core.settings import settings
        from fastapi_fastkit.utils.main import print_error

        # Setup console to capture output
        string_io = io.StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=80)
        original_debug = settings.DEBUG_MODE

        try:
            settings.set_debug_mode(True)

            # when
            print_error("Test error message", console=test_console, show_traceback=True)

            # then
            output = string_io.getvalue()
            assert "Test error message" in output

        finally:
            settings.set_debug_mode(original_debug)

    def test_print_success_function(self) -> None:
        """Test print_success function."""
        # given
        import io

        from rich.console import Console

        from fastapi_fastkit.utils.main import print_success

        # Setup console to capture output
        string_io = io.StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=80)

        # when
        print_success("Test success message", console=test_console)

        # then
        output = string_io.getvalue()
        assert "Test success message" in output

    def test_print_warning_function(self) -> None:
        """Test print_warning function."""
        # given
        import io

        from rich.console import Console

        from fastapi_fastkit.utils.main import print_warning

        # Setup console to capture output
        string_io = io.StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=80)

        # when
        print_warning("Test warning message", console=test_console)

        # then
        output = string_io.getvalue()
        assert "Test warning message" in output

    def test_print_info_function(self) -> None:
        """Test print_info function."""
        # given
        import io

        from rich.console import Console

        from fastapi_fastkit.utils.main import print_info

        # Setup console to capture output
        string_io = io.StringIO()
        test_console = Console(file=string_io, force_terminal=True, width=80)

        # when
        print_info("Test info message", console=test_console)

        # then
        output = string_io.getvalue()
        assert "Test info message" in output

    def test_handle_exception_function(self) -> None:
        """Test handle_exception function."""
        # given
        from fastapi_fastkit.utils.main import handle_exception

        # when & then
        # Should not raise exception
        handle_exception(ValueError("Test exception"), "Custom error message")

    def test_handle_exception_function_no_message(self) -> None:
        """Test handle_exception function without custom message."""
        # given
        from fastapi_fastkit.utils.main import handle_exception

        # when & then
        # Should not raise exception
        handle_exception(ValueError("Test exception"))

    def test_create_info_table_function(self) -> None:
        """Test create_info_table function."""
        # given
        from fastapi_fastkit.utils.main import create_info_table

        # when
        table = create_info_table(
            "Test Information",
            {
                "Key 1": "Value 1",
                "Key 2": "Value 2",
            },
        )

        # then
        assert table.title == "Test Information"

    def test_create_info_table_function_empty_data(self) -> None:
        """Test create_info_table function with empty data."""
        # given
        from fastapi_fastkit.utils.main import create_info_table

        # when
        table = create_info_table("Empty Table", {})

        # then
        assert table.title == "Empty Table"
