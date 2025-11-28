# --------------------------------------------------------------------------
# Selection logic and UI rendering for interactive mode
#
# Provides:
# - Table-based option displays using rich
# - Multi-select prompts
# - Confirmation dialogs
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Any, Dict, List, Optional

from rich.panel import Panel
from rich.table import Table

from fastapi_fastkit.utils.main import console


def render_selection_table(
    title: str, options: Dict[str, str], show_numbers: bool = True
) -> None:
    """
    Render a selection table using rich.

    Args:
        title: Table title
        options: Dictionary of option_key: description
        show_numbers: Whether to show numbered options (for single-select)
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")

    if show_numbers:
        table.add_column("Option", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Description", style="yellow")

    for i, (key, description) in enumerate(options.items(), 1):
        if show_numbers:
            table.add_row(str(i), key, description)
        else:
            table.add_row(key, description)

    console.print(table)


def render_feature_options(
    category: str, options: List[str], descriptions: Dict[str, str]
) -> None:
    """
    Render feature options for multi-select.

    Args:
        category: Feature category name
        options: List of option names
        descriptions: Dictionary of option descriptions
    """
    console.print(f"\n[bold cyan]{category}[/bold cyan]")
    console.print(
        "[dim]Select options by entering numbers (comma-separated, e.g., 1,3,4)[/dim]\n"
    )

    for i, option in enumerate(options, 1):
        desc = descriptions.get(option, "")
        console.print(f"  [cyan]{i}[/cyan]. {option} [dim]{desc}[/dim]")


def multi_select_prompt(
    title: str, options: List[str], descriptions: Optional[Dict[str, str]] = None
) -> List[int]:
    """
    Multi-select prompt with comma-separated input.

    Args:
        title: Prompt title
        options: List of options
        descriptions: Optional descriptions for each option

    Returns:
        List of selected indices (0-based)
    """
    descriptions = descriptions or {}

    console.print(f"\n[bold]{title}[/bold]")
    render_feature_options(title, options, descriptions)

    while True:
        selected = console.input(
            "\n[cyan]Your choice (or press Enter to skip):[/cyan] "
        ).strip()

        if not selected:
            return []

        try:
            # Parse comma-separated numbers
            indices = [int(x.strip()) for x in selected.split(",") if x.strip()]

            # Validate indices
            if all(1 <= idx <= len(options) for idx in indices):
                # Convert to 0-based indices
                return [idx - 1 for idx in indices]
            else:
                console.print(
                    f"[red]Invalid selection. Please enter numbers between 1 and {len(options)}[/red]"
                )
        except ValueError:
            console.print(
                "[red]Invalid input. Please enter comma-separated numbers (e.g., 1,3,4)[/red]"
            )


def confirm_selections(config: Dict[str, Any]) -> bool:
    """
    Display summary and confirm all selections.

    Args:
        config: Complete project configuration

    Returns:
        True if user confirms, False otherwise
    """
    table = Table(
        title="📋 Project Configuration Summary",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    # Basic information
    table.add_row("Project Name", config.get("project_name", "N/A"))
    table.add_row("Author", config.get("author", "N/A"))
    table.add_row("Email", config.get("author_email", "N/A"))
    table.add_row("Description", config.get("description", "N/A"))

    # Template
    if config.get("base_template"):
        table.add_row("Base Template", config["base_template"])

    # Database
    db_info = config.get("database", {})
    if db_info.get("type") != "None":
        table.add_row("Database", db_info.get("type", "None"))

    # Authentication
    auth_type = config.get("authentication", "None")
    if auth_type != "None":
        table.add_row("Authentication", auth_type)

    # Async tasks
    task_type = config.get("async_tasks", "None")
    if task_type != "None":
        table.add_row("Async Tasks", task_type)

    # Caching
    cache_type = config.get("caching", "None")
    if cache_type != "None":
        table.add_row("Caching", cache_type)

    # Monitoring
    monitoring_type = config.get("monitoring", "None")
    if monitoring_type != "None":
        table.add_row("Monitoring", monitoring_type)

    # Testing
    testing_type = config.get("testing", "None")
    if testing_type != "None":
        table.add_row("Testing", testing_type)

    # Utilities
    utilities = config.get("utilities", [])
    if utilities:
        table.add_row("Utilities", ", ".join(utilities))

    # Custom packages
    custom = config.get("custom_packages", [])
    if custom:
        table.add_row("Custom Packages", ", ".join(custom))

    # Package manager
    table.add_row("Package Manager", config.get("package_manager", "uv"))

    console.print("\n")
    console.print(table)
    console.print("\n")

    # Show total dependencies count
    total_deps = len(config.get("all_dependencies", []))
    console.print(f"[bold cyan]Total dependencies to install:[/bold cyan] {total_deps}")

    # Ask for confirmation
    response = (
        console.input(
            "\n[bold yellow]Proceed with project creation? [Y/n]:[/bold yellow] "
        )
        .strip()
        .lower()
    )

    return response in ["y", "yes", ""]


def display_feature_catalog(
    catalog: Dict[str, Dict[str, List[str]]], descriptions: Dict[str, str]
) -> None:
    """
    Display the complete feature catalog.

    Args:
        catalog: Package catalog from settings
        descriptions: Feature descriptions from settings
    """
    panel = Panel(
        "[bold cyan]FastAPI-fastkit Feature Catalog[/bold cyan]\n\n"
        "Available features and their associated packages for interactive project creation.",
        title="📚 Feature Catalog",
        border_style="cyan",
    )
    console.print(panel)

    for category, options in catalog.items():
        if category == "utilities":
            continue  # Skip utilities as they may have empty package lists

        desc = descriptions.get(category, category.title())
        table = Table(title=f"{desc}", show_header=True, header_style="bold yellow")
        table.add_column("Option", style="cyan", no_wrap=True)
        table.add_column("Packages", style="green")

        for option_name, packages in options.items():
            if option_name == "None":
                continue
            pkg_list = (
                ", ".join(packages)
                if packages
                else "[dim](No additional packages)[/dim]"
            )
            table.add_row(option_name, pkg_list)

        console.print("\n")
        console.print(table)
