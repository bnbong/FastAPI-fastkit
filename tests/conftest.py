# --------------------------------------------------------------------------
# The Module configures pytest env.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import pytest

from fastapi_fastkit.core.settings import FastkitConfig


@pytest.fixture(autouse=True, scope="session")
def console() -> None:
    pass


@pytest.fixture(autouse=True, scope="session")
def set_terminal_width() -> None:
    os.environ["COLUMNS"] = str(FastkitConfig.TEST_DEFAULT_TERMINAL_WIDTH)
