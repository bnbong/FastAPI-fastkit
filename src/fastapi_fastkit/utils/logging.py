# --------------------------------------------------------------------------
# The Module defines custom console logging operations.
#
# Will be added later versions of FastAPI-fastkit,
#   when log collection is implemented.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import logging
import os
import sys
from datetime import datetime
from functools import lru_cache
from typing import Dict, Optional

from rich.console import Console
from rich.logging import RichHandler

from fastapi_fastkit.core.settings import FastkitConfig


class DebugFileHandler(logging.Handler):
    """Custom logging handler for debug mode that captures all output."""

    def __init__(self, log_file_path: str):
        super().__init__()
        self.log_file_path = log_file_path
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_entry = self.format(record)
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(f"{log_entry}\n")
        except (OSError, PermissionError, UnicodeError) as e:
            # More specific exception handling
            self.handleError(record)
            # Optionally log the error to stderr if it's critical
            print(f"Logging error: {e}", file=sys.stderr)


class DebugOutputCapture:
    """Captures stdout and stderr to log file in debug mode."""

    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def __enter__(self) -> "DebugOutputCapture":
        # Create a custom writer that writes to both original output and log file
        class TeeWriter:
            def __init__(
                self, original: object, log_file: str, stream_type: str
            ) -> None:
                self.original = original
                self.log_file = log_file
                self.stream_type = stream_type

            def write(self, text: str) -> None:
                # Write to original stream
                if hasattr(self.original, "write") and hasattr(self.original, "flush"):
                    try:
                        self.original.write(text)
                        self.original.flush()
                    except (OSError, UnicodeError):
                        pass  # Fail silently for original stream errors

                # Write to log file with timestamp and stream type
                if text.strip():  # Only log non-empty lines
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        with open(self.log_file, "a", encoding="utf-8") as f:
                            f.write(f"[{timestamp}] [{self.stream_type}] {text}")
                            if not text.endswith("\n"):
                                f.write("\n")
                    except (OSError, PermissionError, UnicodeError):
                        pass  # Fail silently if logging fails

            def flush(self) -> None:
                if hasattr(self.original, "flush"):
                    try:
                        self.original.flush()
                    except (OSError, UnicodeError):
                        pass  # Fail silently

        sys.stdout = TeeWriter(self.original_stdout, self.log_file_path, "STDOUT")
        sys.stderr = TeeWriter(self.original_stderr, self.log_file_path, "STDERR")
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr


_logger_cache: Dict[str, logging.Logger] = {}


def setup_logging(
    settings: FastkitConfig, terminal_width: Optional[int] = None
) -> Optional[DebugOutputCapture]:
    """
    Setup logging for fastapi-fastkit.

    :param settings: FastkitConfig instance
    :param terminal_width: Optional terminal width for Rich console
    :return: DebugOutputCapture instance if debug mode is enabled, None otherwise
    """
    logger = logging.getLogger("fastapi-fastkit")
    console = Console(width=terminal_width) if terminal_width else None
    formatter = logging.Formatter("%(message)s")

    rich_handler = RichHandler(
        show_time=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
        show_path=False,
        console=console,
    )
    rich_handler.setFormatter(formatter)

    logger.setLevel(settings.LOGGING_LEVEL)
    logger.propagate = False

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    logger.addHandler(rich_handler)

    # If debug mode is enabled, add file logging
    debug_capture = None
    if settings.DEBUG_MODE:
        file_handler = DebugFileHandler(settings.LOG_FILE_PATH)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(file_handler)

        # Create debug capture for stdout/stderr
        debug_capture = DebugOutputCapture(settings.LOG_FILE_PATH)

    return debug_capture


@lru_cache(maxsize=128)
def get_logger(name: str = "fastapi-fastkit") -> logging.Logger:
    """
    Get a logger instance with caching for better performance.

    :param name: Logger name
    :return: Logger instance
    """
    # Double-check with cache dictionary for additional caching layer
    if name not in _logger_cache:
        _logger_cache[name] = logging.getLogger(name)
    return _logger_cache[name]


def debug_log(
    message: str, level: str = "info", logger_name: str = "fastapi-fastkit"
) -> None:
    """
    Centralized debug logging function to reduce code duplication.

    :param message: Message to log
    :param level: Log level (info, warning, error, debug)
    :param logger_name: Logger name to use
    """
    from fastapi_fastkit.core.settings import settings

    if settings.DEBUG_MODE:
        logger = get_logger(logger_name)
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message)


def clear_logger_cache() -> None:
    """Clear the logger cache (useful for testing)."""
    global _logger_cache
    _logger_cache.clear()
    # Also clear LRU cache
    get_logger.cache_clear()
