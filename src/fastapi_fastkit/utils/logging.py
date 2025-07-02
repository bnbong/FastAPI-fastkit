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
from typing import Union

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
        except Exception:
            self.handleError(record)


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
                    self.original.write(text)
                    self.original.flush()

                # Write to log file with timestamp and stream type
                if text.strip():  # Only log non-empty lines
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        with open(self.log_file, "a", encoding="utf-8") as f:
                            f.write(f"[{timestamp}] [{self.stream_type}] {text}")
                            if not text.endswith("\n"):
                                f.write("\n")
                    except Exception:
                        pass  # Fail silently if logging fails

            def flush(self) -> None:
                if hasattr(self.original, "flush"):
                    self.original.flush()

        sys.stdout = TeeWriter(self.original_stdout, self.log_file_path, "STDOUT")
        sys.stderr = TeeWriter(self.original_stderr, self.log_file_path, "STDERR")
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr


def setup_logging(
    settings: FastkitConfig, terminal_width: Union[int, None] = None
) -> Union[DebugOutputCapture, None]:
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

    # Clear existing handlers
    logger.handlers.clear()
    logger.addHandler(rich_handler)

    # If debug mode is enabled, add file logging
    debug_capture = None
    if settings.DEBUG_MODE:
        # Create logs directory in the package source
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = os.path.join(logs_dir, f"fastkit_debug_{timestamp}.log")

        # Add file handler for logger
        file_handler = DebugFileHandler(log_file_path)
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Create output capture for stdout/stderr
        debug_capture = DebugOutputCapture(log_file_path)

        # Log the start of debug session
        logger.info(f"Debug mode enabled. Logging to: {log_file_path}")
        logger.info(f"FastAPI-fastkit CLI session started at {datetime.now()}")

    return debug_capture


def get_logger(name: str = "fastapi-fastkit") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
