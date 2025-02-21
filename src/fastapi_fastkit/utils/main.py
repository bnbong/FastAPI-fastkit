# --------------------------------------------------------------------------
# The Module defines utility functions for FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import re
from typing import Any

import click
from click.core import Context
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from fastapi_fastkit import console

REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"


def print_error(message: str, title: str = "Error", console: Console = console) -> None:
    """Print an error message with specified output style."""
    error_text = Text()
    error_text.append("❌ ", style="bold red")
    error_text.append(message)
    console.print(Panel(error_text, border_style="red", title=title))


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
    data: dict[str, str],
    show_header: bool = False,
    console: Console = console,
) -> Table:
    """Create a table for displaying information."""
    table = Table(title=title, show_header=show_header, title_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

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
