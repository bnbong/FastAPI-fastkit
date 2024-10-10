import sys
import pytest

# from rich.console import Console
# from typing import Generator

from fastapi_fastkit.utils.logging import setup_logging
from fastapi_fastkit.core.settings import FastkitConfig


@pytest.fixture(autouse=True, scope="session")
def console() -> None:
    setup_logging(terminal_width=FastkitConfig.TEST_DEFAULT_TERMINAL_WIDTH)

