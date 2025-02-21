# --------------------------------------------------------------------------
# The Module configures pytest env.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import shutil
from io import StringIO
from typing import Generator

import pytest
from rich.console import Console

from fastapi_fastkit.core.settings import FastkitConfig


@pytest.fixture(autouse=True, scope="session")
def temp_dir() -> Generator[str, None, None]:
    """
    Fixture that creates a temporary directory for test cases and yields its path.
    After tests are done, the directory is removed.
    """
    current_workspace = os.path.dirname(
        os.path.abspath(__file__)
    )  # use test/ directory as workspace
    temp_dir = os.path.join(current_workspace, "temp_test_workspace")
    os.makedirs(temp_dir, exist_ok=True)
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(autouse=True, scope="session")
def set_terminal_width() -> None:
    """
    Fixture to set the terminal width for tests.
    """
    os.environ["COLUMNS"] = str(FastkitConfig.TEST_DEFAULT_TERMINAL_WIDTH)


@pytest.fixture(autouse=True, scope="session")
def console() -> Generator[Console, None, None]:
    """
    Fixture to create a Console instance for tests.
    """
    yield Console(file=StringIO(), width=FastkitConfig.TEST_DEFAULT_TERMINAL_WIDTH)
