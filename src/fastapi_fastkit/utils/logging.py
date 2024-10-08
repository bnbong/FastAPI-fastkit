# TODO : logger will run at only debug mode.
# --------------------------------------------------------------------------
# The Module defines console logging operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import logging

from typing import Union

from rich.console import Console
from rich.logging import RichHandler

from fastapi_fastkit.core.settings import FastkitConfig


def setup_logging(terminal_width: Union[int, None] = None) -> None:
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

    logger.setLevel(FastkitConfig.LOGGING_LEVEL)
    logger.propagate = False
