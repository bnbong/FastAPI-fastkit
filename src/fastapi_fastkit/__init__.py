__version__ = "0.1.2"

import os

from rich.console import Console

if "PYTEST_CURRENT_TEST" in os.environ:
    console = Console(no_color=True)
else:
    console = Console()
