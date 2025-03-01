# --------------------------------------------------------------------------
# The Module defines utility functions for FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import re
import traceback
from typing import Any, Optional

import click
from click.core import Context
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from fastapi_fastkit import console
from fastapi_fastkit.core.settings import settings

REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"


def print_error(
    message: str,
    title: str = "Error",
    console: Console = console,
    show_traceback: bool = False,
) -> None:
    """Print an error message with specified output style."""
    error_text = Text()
    error_text.append("❌ ", style="bold red")
    error_text.append(message)
    console.print(Panel(error_text, border_style="red", title=title))

    if show_traceback and settings.DEBUG_MODE:
        console.print("[bold yellow]Stack trace:[/bold yellow]")
        console.print(traceback.format_exc())


def handle_exception(e: Exception, message: Optional[str] = None) -> None:
    """
    Handle exception and print appropriate error message.

    :param e: The exception that occurred
    :param message: Optional custom error message
    """
    error_msg = message or f"Error: {str(e)}"

    # Show traceback if in debug mode
    print_error(error_msg, show_traceback=True)


def print_success(
    message: str, title: str = "Success", console: Console = console
) -> None:
    """Print a success message with specified output style."""
    success_text = Text()
    success_text.append("✨ ", style="bold yellow")
    success_text.append(message, style="bold green")
    console.print(Panel(success_text, border_style="green", title=title))


def print_warning(
    message: str, title: str = "Warning", console: Console = console
) -> None:
    """Print a warning message with specified output style."""
    warning_text = Text()
    warning_text.append("⚠️ ", style="bold yellow")
    warning_text.append(message)
    console.print(Panel(warning_text, border_style="yellow", title=title))


def print_info(message: str, title: str = "Info", console: Console = console) -> None:
    """Print an info message with specified output style."""
    info_text = Text()
    info_text.append("ℹ ", style="bold blue")
    info_text.append(message)
    console.print(Panel(info_text, border_style="blue", title=title))


def create_info_table(
    title: str,
    data: Optional[dict[str, str]] = None,
    show_header: bool = False,
    console: Console = console,
) -> Table:
    """Create a table for displaying information."""
    table = Table(title=title, show_header=show_header, title_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    if data:
        for key, value in data.items():
            table.add_row(key, value)

    return table


def validate_email(ctx: Context, param: Any, value: Any) -> Any:
    """Validate email format."""
    try:
        if not re.match(REGEX, value):
            raise ValueError(value)
        return value
    except ValueError as e:
        print_error(f"Incorrect email address given: {e}")
        value = click.prompt(param.prompt)
        return validate_email(ctx, param, value)


def is_fastkit_project(project_dir: str) -> bool:
    """
    Check if the project was created with fastkit.
    Inspects the contents of the setup.py file.

    :param project_dir: Project directory
    :return: True if the project was created with fastkit, False otherwise
    """
    setup_py = os.path.join(project_dir, "setup.py")
    if not os.path.exists(setup_py):
        return False

    try:
        with open(setup_py, "r") as f:
            content = f.read()
            return "FastAPI-fastkit" in content
    except:
        return False
