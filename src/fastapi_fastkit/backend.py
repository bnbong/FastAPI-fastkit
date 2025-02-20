# --------------------------------------------------------------------------
# The Module defines backend operations for FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import re
import subprocess
from logging import getLogger
from typing import Any

import click
from click.core import Context
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from fastapi_fastkit.core.exceptions import BackendExceptions, TemplateExceptions

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


def print_info(message: str, title: str = "Info") -> None:
    """Print an info message with specified output style."""
    info_text = Text()
    info_text.append("ℹ ", style="bold blue")
    info_text.append(message)
    console.print(Panel(info_text, border_style="blue", title=title))


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
    # TODO : add main.py location at parameter & find settings.py, config.py, etc and inject project name init
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


def create_venv(project_dir: str) -> str:
    """Create a virtual environment."""
    try:
        with console.status("[bold green]Setting up project environment..."):
            console.print("[yellow]Creating virtual environment...[/yellow]")
            venv_path = os.path.join(project_dir, ".venv")
            subprocess.run(["python", "-m", "venv", venv_path], check=True)

        if os.name == "nt":
            activate_venv = f"    {os.path.join(venv_path, 'Scripts', 'activate.bat')}"
        else:
            activate_venv = f"    source {os.path.join(venv_path, 'bin', 'activate')}"
            print_info(
                "venv created at "
                + venv_path
                + "\nTo activate the virtual environment, run:\n\n"
                + activate_venv,
            )
        return venv_path

    except Exception as e:
        print_error(f"Error during venv creation: {e}")
        raise BackendExceptions("Failed to create venv")


def install_dependencies(project_dir: str, venv_path: str) -> None:
    """Install project dependencies in the virtual environment."""
    try:
        if os.name == "nt":  # Windows
            pip_path = os.path.join(venv_path, "Scripts", "pip")
        else:  # Linux/Mac
            pip_path = os.path.join(venv_path, "bin", "pip")

        with console.status("[bold green]Installing dependencies..."):
            subprocess.run(
                [pip_path, "install", "-r", "requirements.txt"],
                cwd=project_dir,
                check=True,
            )

    except Exception as e:
        print_error(f"Error during dependency installation: {e}")
        raise BackendExceptions("Failed to install dependencies")


# TODO : modify this function
# def read_template_stack() -> Union[list, None]:
#     pass
