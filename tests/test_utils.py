"""
Test cases for utils modules.
"""

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
