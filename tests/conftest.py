# --------------------------------------------------------------------------
# The Module configures pytest env.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from io import StringIO
from typing import Generator

import pytest
from rich.console import Console

from fastapi_fastkit.core.settings import FastkitConfig


@pytest.fixture(autouse=True, scope="session")
def temp_dir(tmp_path_factory: pytest.TempPathFactory) -> Generator[str, None, None]:
    """
    Fixture that yields a session-scoped temporary workspace path.

    ``tmp_path_factory`` is used instead of a fixed ``tests/temp_test_workspace``
    directory so parallel/concurrent test runs never share (or delete) each
    other's workspace, and so pytest — not a ``shutil.rmtree`` in teardown —
    owns the cleanup of the last few runs' artifacts.
    """
    yield str(tmp_path_factory.mktemp("fastkit_workspace"))


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
