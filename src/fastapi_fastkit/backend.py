# --------------------------------------------------------------------------
# The Module defines backend operations for FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import re
from logging import getLogger
from typing import Any

import click
from click.core import Context
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from fastapi_fastkit.core.exceptions import TemplateExceptions

from . import console

logger = getLogger(__name__)

REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"


def print_error(message: str, title: str = "Error") -> None:
    """Print an error message with specified output style."""
    error_text = Text()
    error_text.append("❌ ", style="bold red")
    error_text.append(message)
    console.print(Panel(error_text, border_style="red", title=title))


def print_success(message: str, title: str = "Success") -> None:
    """Print a success message with specified output style."""
    success_text = Text()
    success_text.append("✨ ", style="bold yellow")
    success_text.append(message, style="bold green")
    console.print(Panel(success_text, border_style="green", title=title))


def print_warning(message: str, title: str = "Warning") -> None:
    """Print a warning message with specified output style."""
    warning_text = Text()
    warning_text.append("⚠️ ", style="bold yellow")
    warning_text.append(message)
    console.print(Panel(warning_text, border_style="yellow", title=title))


def create_info_table(
    title: str, data: dict[str, str], show_header: bool = False
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


def inject_project_metadata(
    target_dir: str,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
) -> None:
    """Inject project metadata."""
    try:
        main_py_path = os.path.join(target_dir, "main.py")
        setup_py_path = os.path.join(target_dir, "setup.py")

        with open(main_py_path, "r+") as f:
            content = f.read()
            content = content.replace("app_title", f'"{project_name}"')
            content = content.replace("app_description", f'"{description}"')
            f.seek(0)
            f.write(content)
            f.truncate()

        with open(setup_py_path, "r+") as f:
            content = f.read()
            content = content.replace("<project_name>", project_name, 1)
            content = content.replace("<description>", description, 1)
            content = content.replace("<author>", author, 1)
            content = content.replace("<author_email>", author_email, 1)
            f.seek(0)
            f.write(content)
            f.truncate()
    except Exception as e:
        print_error(f"Error during metadata injection: {e}")
        raise TemplateExceptions("Failed to inject metadata")


# TODO : modify this function
# def read_template_stack() -> Union[list, None]:
#     pass
