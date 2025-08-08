# --------------------------------------------------------------------------
# Testcases of rich console operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import logging
import os
import sys
from io import StringIO
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from fastapi_fastkit.utils.logging import (
    DebugFileHandler,
    DebugOutputCapture,
    clear_logger_cache,
    debug_log,
    get_logger,
    setup_logging,
)


class TestCLI:
    def setup_method(self) -> None:
        self.runner = MagicMock()  # CliRunner is not used in this test file, so mock it
        self.current_workspace = os.getcwd()
        self.stdout = StringIO()
        self.old_stdout = sys.stdout
        sys.stdout = self.stdout

    def teardown_method(self, console: Any) -> None:
        os.chdir(self.current_workspace)
        sys.stdout = self.old_stdout

    def test_success_message(self, console: Any) -> None:
        # given
        from fastapi_fastkit.utils.main import print_success

        test_message = "this is success test"

        # when
        print_success(message=test_message, console=console)
        output = console.file.getvalue()

        # then
        assert "Success" in output and test_message in output

    def test_error_message(self, console: Any) -> None:
        # given
        from fastapi_fastkit.utils.main import print_error

        test_message = "this is error test"

        # when
        print_error(message=test_message, console=console)
        output = console.file.getvalue()

        # then
        assert "Error" in output and test_message in output

    def test_warning_message(self, console: Any) -> None:
        # given
        from fastapi_fastkit.utils.main import print_warning

        test_message = "this is warning test"

        # when
        print_warning(message=test_message, console=console)
        output = console.file.getvalue()

        # then
        assert "Warning" in output and test_message in output

    def test_info_message(self, console: Any) -> None:
        # given
        from fastapi_fastkit.utils.main import print_info

        test_message = "this is info test"

        # when
        print_info(message=test_message, console=console)
        output = console.file.getvalue()

        # then
        assert "Info" in output and test_message in output


class TestDebugFileHandler:
    """Test cases for DebugFileHandler class."""

    def test_debug_file_handler_init(self, temp_dir: str) -> None:
        """Test DebugFileHandler initialization."""
        # given
        log_file_path = os.path.join(temp_dir, "logs", "test.log")

        # when
        handler = DebugFileHandler(log_file_path)

        # then
        assert handler.log_file_path == log_file_path
        assert os.path.exists(os.path.dirname(log_file_path))

    def test_debug_file_handler_emit_success(self, temp_dir: str) -> None:
        """Test DebugFileHandler emit method with successful write."""
        # given
        log_file_path = os.path.join(temp_dir, "logs", "test.log")
        handler = DebugFileHandler(log_file_path)

        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # when
        handler.emit(record)

        # then
        assert os.path.exists(log_file_path)
        with open(log_file_path, "r") as f:
            content = f.read()
            assert "Test message" in content

    def test_debug_file_handler_emit_permission_error(self, temp_dir: str) -> None:
        """Test DebugFileHandler emit method with permission error."""
        # given
        log_file_path = os.path.join(temp_dir, "readonly", "test.log")
        handler = DebugFileHandler(log_file_path)

        # Create readonly directory
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        if os.name != "nt":  # Skip on Windows
            os.chmod(os.path.dirname(log_file_path), 0o444)

        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        try:
            # when & then
            # Should not raise exception, but handle it gracefully
            handler.emit(record)
        finally:
            if os.name != "nt":
                os.chmod(os.path.dirname(log_file_path), 0o755)


class TestDebugOutputCapture:
    """Test cases for DebugOutputCapture class."""

    def test_debug_output_capture_init(self, temp_dir: str) -> None:
        """Test DebugOutputCapture initialization."""
        # given
        log_file_path = os.path.join(temp_dir, "debug.log")

        # when
        capture = DebugOutputCapture(log_file_path)

        # then
        assert capture.log_file_path == log_file_path
        # Note: original_stdout and original_stderr are not set until __enter__ is called

    def test_debug_output_capture_context_manager(self, temp_dir: str) -> None:
        """Test DebugOutputCapture as context manager."""
        # given
        log_file_path = os.path.join(temp_dir, "debug.log")
        capture = DebugOutputCapture(log_file_path)
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        # when & then
        with capture:
            print("Test stdout")
            print("Test stderr", file=sys.stderr)

        # After exiting context, should restore original streams
        assert sys.stdout == original_stdout
        assert sys.stderr == original_stderr

    def test_debug_output_capture_enter_exit(self, temp_dir: str) -> None:
        """Test DebugOutputCapture enter and exit methods directly."""
        # given
        log_file_path = os.path.join(temp_dir, "debug.log")
        capture = DebugOutputCapture(log_file_path)
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        # when
        capture.__enter__()

        # then
        assert capture.original_stdout == original_stdout
        assert capture.original_stderr == original_stderr

        # when
        capture.__exit__(None, None, None)

        # then
        assert sys.stdout == original_stdout
        assert sys.stderr == original_stderr


class TestLoggingFunctions:
    """Test cases for logging utility functions."""

    def test_get_logger_function(self) -> None:
        """Test get_logger function."""
        # given & when
        logger = get_logger("test-logger")

        # then
        assert logger.name == "test-logger"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_function_caching(self) -> None:
        """Test get_logger function caching behavior."""
        # given & when
        logger1 = get_logger("cached-logger")
        logger2 = get_logger("cached-logger")

        # then
        assert logger1 is logger2  # Should be the same instance due to caching

    def test_debug_log_function_debug_mode_on(self) -> None:
        """Test debug_log function when debug mode is enabled."""
        # given
        from fastapi_fastkit.core.settings import settings

        original_debug = settings.DEBUG_MODE

        try:
            settings.set_debug_mode(True)

            # when & then
            # Should not raise exception
            debug_log("Test debug message", "info")
            debug_log("Test warning message", "warning")
            debug_log("Test error message", "error")

        finally:
            settings.set_debug_mode(original_debug)

    def test_debug_log_function_debug_mode_off(self) -> None:
        """Test debug_log function when debug mode is disabled."""
        # given
        from fastapi_fastkit.core.settings import settings

        original_debug = settings.DEBUG_MODE

        try:
            settings.set_debug_mode(False)

            # when & then
            # Should not raise exception and should not log anything
            debug_log("Test debug message", "info")

        finally:
            settings.set_debug_mode(original_debug)

    def test_debug_log_function_invalid_level(self) -> None:
        """Test debug_log function with invalid log level."""
        # given
        from fastapi_fastkit.core.settings import settings

        original_debug = settings.DEBUG_MODE

        try:
            settings.set_debug_mode(True)

            # when & then
            # Should fall back to info level and not raise exception
            debug_log("Test message", "invalid_level")

        finally:
            settings.set_debug_mode(original_debug)

    def test_clear_logger_cache_function(self) -> None:
        """Test clear_logger_cache function."""
        # given
        logger1 = get_logger("cache-test-logger")

        # Verify cache info before clearing
        cache_info_before = get_logger.cache_info()

        # when
        clear_logger_cache()

        # then
        cache_info_after = get_logger.cache_info()
        # Cache should be cleared (hits and misses reset, currsize should be 0)
        assert cache_info_after.currsize == 0

        # Getting the same logger name should create a cache miss
        logger2 = get_logger("cache-test-logger")
        assert isinstance(logger2, logging.Logger)

    def test_setup_logging_function_debug_mode(self, temp_dir: str) -> None:
        """Test setup_logging function with debug mode."""
        # given
        from fastapi_fastkit.core.settings import FastkitConfig

        test_settings = FastkitConfig()
        test_settings.set_debug_mode(True)
        test_settings.LOG_FILE_PATH = os.path.join(temp_dir, "test.log")

        # when
        capture = setup_logging(settings=test_settings)

        # then
        assert capture is not None
        assert isinstance(capture, DebugOutputCapture)

    def test_setup_logging_function_no_debug_mode(self) -> None:
        """Test setup_logging function without debug mode."""
        # given
        from fastapi_fastkit.core.settings import FastkitConfig

        test_settings = FastkitConfig()
        test_settings.set_debug_mode(False)

        # when
        capture = setup_logging(settings=test_settings)

        # then
        assert capture is None
