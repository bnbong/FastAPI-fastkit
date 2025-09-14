# --------------------------------------------------------------------------
# The Module defines utility functions for FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import re
import traceback
from typing import Any, Dict, Optional

import click
from click.core import Context
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.logging import debug_log, get_logger

logger = get_logger(__name__)

# Email validation regex pattern
REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"


def get_optimal_console_size() -> tuple[int, int]:
    """
    Get optimal console size based on terminal dimensions.

    Returns:
        tuple: (width, height) - optimal console dimensions
    """
    try:
        # Get terminal size
        terminal_size = os.get_terminal_size()
        width = terminal_size.columns
        height = terminal_size.lines

        # Set minimum and maximum constraints
        min_width = 80
        max_width = 120
        min_height = 24

        # Calculate optimal width (80% of terminal width, but within constraints)
        optimal_width = max(min_width, min(max_width, int(width * 0.8)))
        # Calculate optimal height (leave some space for prompt and buffer)
        optimal_height = max(min_height, height - 5)

        return optimal_width, optimal_height
    except (OSError, ValueError):
        # Fallback to default size if terminal size detection fails
        return 80, 24


def create_adaptive_console() -> Console:
    """
    Create a console instance with adaptive sizing based on terminal dimensions.

    Returns:
        Console: Rich console instance with optimal sizing
    """
    if "PYTEST_CURRENT_TEST" in os.environ:
        return Console(no_color=True)

    width, height = get_optimal_console_size()
    return Console(width=width, height=height)


# Initialize console with adaptive sizing
console = create_adaptive_console()


def _get_adaptive_panel_width(message: str) -> int:
    """
    Calculate optimal panel width based on message length and terminal size.

    :param message: Message content
    :return: Optimal panel width
    """
    optimal_width, _ = get_optimal_console_size()
    # Use message length + padding, but constrain to reasonable bounds
    min_width = min(len(message) + 10, optimal_width - 4)
    return max(40, min_width)  # Minimum 40 chars, leave margin for borders


def print_error(
    message: str,
    title: str = "Error",
    console: Console = console,
    show_traceback: bool = False,
) -> None:
    """
    Print an error message with specified output style.

    :param message: Error message to display
    :param title: Title for the error panel
    :param console: Rich console instance
    :param show_traceback: Whether to show stack trace in debug mode
    """
    error_text = Text()
    error_text.append("❌ ", style="bold red")
    error_text.append(message)

    panel_width = _get_adaptive_panel_width(message)
    console.print(Panel(error_text, border_style="red", title=title, width=panel_width))

    # Log error for debugging purposes (internal logging)
    debug_log(f"Error: {message}", "error")

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

    # Log exception for debugging purposes (internal logging)
    debug_log(f"Exception occurred: {error_msg}", "error")

    # Show traceback if in debug mode
    print_error(error_msg, show_traceback=True)


def print_success(
    message: str, title: str = "Success", console: Console = console
) -> None:
    """
    Print a success message with specified output style.

    :param message: Success message to display
    :param title: Title for the success panel
    :param console: Rich console instance
    """
    success_text = Text()
    success_text.append("✨ ", style="bold yellow")
    success_text.append(message, style="bold green")

    panel_width = _get_adaptive_panel_width(message)
    console.print(
        Panel(success_text, border_style="green", title=title, width=panel_width)
    )


def print_warning(
    message: str, title: str = "Warning", console: Console = console
) -> None:
    """
    Print a warning message with specified output style.

    :param message: Warning message to display
    :param title: Title for the warning panel
    :param console: Rich console instance
    """
    warning_text = Text()
    warning_text.append("⚠️ ", style="bold yellow")
    warning_text.append(message)

    panel_width = _get_adaptive_panel_width(message)
    console.print(
        Panel(warning_text, border_style="yellow", title=title, width=panel_width)
    )


def print_info(message: str, title: str = "Info", console: Console = console) -> None:
    """
    Print an info message with specified output style.

    :param message: Info message to display
    :param title: Title for the info panel
    :param console: Rich console instance
    """
    info_text = Text()
    info_text.append("ℹ ", style="bold blue")
    info_text.append(message)

    panel_width = _get_adaptive_panel_width(message)
    console.print(Panel(info_text, border_style="blue", title=title, width=panel_width))


def create_info_table(
    title: str,
    data: Optional[Dict[str, str]] = None,
    show_header: bool = False,
    console: Console = console,
) -> Table:
    """
    Create a table for displaying information that never truncates text.

    :param title: Title for the table
    :param data: Dictionary of data to populate the table
    :param show_header: Whether to show table headers
    :param console: Rich console instance
    :return: Configured Rich Table instance
    """
    # Calculate exact content lengths if data exists
    if data:
        max_field_length = max(len(str(key)) for key in data.keys())
        max_value_length = max(len(str(value)) for value in data.values())

        # Set column widths to exactly match the longest content
        # Add small padding to ensure content fits comfortably
        field_width = max_field_length + 2
        value_width = max_value_length + 2
    else:
        # Default widths for empty tables
        field_width = 15
        value_width = 30

    # Create table that prioritizes full text display over terminal fitting
    table = Table(
        title=title,
        show_header=show_header,
        title_style="bold magenta",
        expand=False,  # Never expand to terminal width
        width=None,  # Let table size itself based on content
        pad_edge=False,  # Reduce padding to save space
    )

    # Add columns with settings that prevent any truncation
    table.add_column(
        "Field",
        style="cyan",
        no_wrap=False,  # Allow wrapping instead of truncating
        width=field_width,  # Exact width for content
        min_width=field_width,  # Minimum width to prevent shrinking
        max_width=None,  # No maximum width limit
        overflow="fold",  # Fold text instead of truncating
    )
    table.add_column(
        "Value",
        style="green",
        no_wrap=False,  # Allow wrapping instead of truncating
        width=value_width,  # Exact width for content
        min_width=value_width,  # Minimum width to prevent shrinking
        max_width=None,  # No maximum width limit
        overflow="fold",  # Fold text instead of truncating
    )

    if data:
        for key, value in data.items():
            table.add_row(str(key), str(value))

    return table


def validate_email(ctx: Context, param: Any, value: Any) -> Any:
    """
    Validate email format using regex pattern.

    :param ctx: Click context
    :param param: Click parameter
    :param value: Email value to validate
    :return: Validated email value
    :raises ValueError: If email format is invalid
    """
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
    Inspects the contents of the setup.py file for FastAPI-fastkit markers.

    :param project_dir: Path to the project directory
    :return: True if the project was created with fastkit, False otherwise
    """
    setup_py = os.path.join(project_dir, "setup.py")
    if not os.path.exists(setup_py):
        return False

    try:
        with open(setup_py, "r", encoding="utf-8") as f:
            content = f.read()
            return "FastAPI-fastkit" in content
    except (OSError, UnicodeDecodeError):
        return False
