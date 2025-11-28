# --------------------------------------------------------------------------
# Interactive prompt definitions for FastAPI-fastkit CLI
#
# Provides user-facing prompts for:
# - Basic project information
# - Template selection
# - Database selection
# - Authentication method
# - Additional features
# - Testing configuration
# - Deployment options
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Any, Dict, List, Optional, cast

import click
from rich.panel import Panel

from fastapi_fastkit.utils.main import console, print_error

from .selectors import render_selection_table
from .validators import validate_email_format, validate_project_name


def prompt_basic_info() -> Dict[str, str]:
    """
    Prompt for basic project information.

    Returns:
        Dictionary with project_name, author, author_email, description
    """
    console.print("\n[bold cyan]📝 Project Information[/bold cyan]")
    console.print(
        "[dim]Let's start with some basic information about your project[/dim]\n"
    )

    # Project name
    while True:
        project_name = click.prompt("Project name", type=str)
        is_valid, error = validate_project_name(project_name)
        if is_valid:
            break
        print_error(error or "Invalid project name")

    # Author
    author = click.prompt("Author name", type=str)

    # Email
    while True:
        author_email = click.prompt("Author email", type=str)
        if validate_email_format(author_email):
            break
        print_error("Invalid email format. Please enter a valid email address.")

    # Description
    description = click.prompt("Project description", type=str)

    return {
        "project_name": project_name,
        "author": author,
        "author_email": author_email,
        "description": description,
    }


def prompt_template_selection(settings: Any) -> Optional[str]:
    """
    Prompt for base template selection.

    Args:
        settings: FastkitConfig instance

    Returns:
        Template name or None for empty project
    """
    import os

    console.print("\n[bold cyan]📦 Base Template Selection[/bold cyan]")
    console.print("[dim]Choose a base template or start from scratch[/dim]\n")

    template_dir = settings.FASTKIT_TEMPLATE_ROOT
    excluded_dirs = ["__pycache__", "modules", "fastapi-empty"]

    templates = [
        d
        for d in os.listdir(template_dir)
        if os.path.isdir(os.path.join(template_dir, d)) and d not in excluded_dirs
    ]

    # Add "Empty Project" option
    options = {"Empty Project": "Start with minimal FastAPI setup"}

    # Add available templates
    for template in templates:
        readme_path = os.path.join(template_dir, template, "README.md-tpl")
        description = "No description"
        if os.path.exists(readme_path):
            with open(readme_path, "r") as f:
                first_line = f.readline().strip()
                if first_line.startswith("# "):
                    description = first_line[2:]
        options[template] = description

    render_selection_table("Available Templates", options)

    choice = click.prompt(
        "\nSelect template",
        type=click.IntRange(1, len(options)),
        default=1,
    )

    selected_key = list(options.keys())[choice - 1]

    return cast(
        Optional[str], selected_key if selected_key != "Empty Project" else None
    )


def prompt_database_selection(settings: Any) -> Dict[str, Any]:
    """
    Prompt for database selection.

    Args:
        settings: FastkitConfig instance

    Returns:
        Dictionary with type and packages
    """
    console.print("\n[bold cyan]🗄️  Database Selection[/bold cyan]")
    console.print("[dim]Choose your database backend[/dim]\n")

    db_catalog = settings.PACKAGE_CATALOG["database"]
    options = {
        name: f"Packages: {', '.join(pkgs) if pkgs else 'None'}"
        for name, pkgs in db_catalog.items()
    }

    render_selection_table("Database Options", options)

    choice = click.prompt(
        "\nSelect database",
        type=click.IntRange(1, len(options)),
        default=len(options),  # Default to "None"
    )

    selected_type = list(options.keys())[choice - 1]

    return {
        "type": selected_type,
        "packages": db_catalog[selected_type],
    }


def prompt_authentication_selection(settings: Any) -> str:
    """
    Prompt for authentication method.

    Args:
        settings: FastkitConfig instance

    Returns:
        Authentication type name
    """
    console.print("\n[bold cyan]🔐 Authentication Selection[/bold cyan]")
    console.print("[dim]Choose your authentication strategy[/dim]\n")

    auth_catalog = settings.PACKAGE_CATALOG["authentication"]
    options = {}

    for name, pkgs in auth_catalog.items():
        if name == "None":
            options[name] = "No authentication"
        elif name == "JWT":
            options[name] = "JSON Web Tokens (recommended for APIs)"
        elif name == "OAuth2":
            options[name] = "OAuth2 with authlib"
        elif name == "FastAPI-Users":
            options[name] = "Complete user management system (includes JWT)"
        elif name == "Session-based":
            options[name] = "Traditional session-based authentication"
        else:
            options[name] = f"Packages: {', '.join(pkgs)}"

    render_selection_table("Authentication Options", options)

    choice = click.prompt(
        "\nSelect authentication method",
        type=click.IntRange(1, len(options)),
        default=len(options),  # Default to "None"
    )

    return cast(str, list(options.keys())[choice - 1])


def prompt_async_tasks_selection(settings: Any) -> str:
    """
    Prompt for async task queue selection.

    Args:
        settings: FastkitConfig instance

    Returns:
        Task queue type name
    """
    console.print("\n[bold cyan]⚡ Background Tasks Selection[/bold cyan]")
    console.print("[dim]Choose a task queue for background processing[/dim]\n")

    task_catalog = settings.PACKAGE_CATALOG["async_tasks"]
    options = {
        name: f"Packages: {', '.join(pkgs) if pkgs else 'None'}"
        for name, pkgs in task_catalog.items()
    }

    render_selection_table("Task Queue Options", options)

    choice = click.prompt(
        "\nSelect task queue",
        type=click.IntRange(1, len(options)),
        default=len(options),  # Default to "None"
    )

    return cast(str, list(options.keys())[choice - 1])


def prompt_caching_selection(settings: Any) -> str:
    """
    Prompt for caching selection.

    Args:
        settings: FastkitConfig instance

    Returns:
        Caching type name
    """
    console.print("\n[bold cyan]💾 Caching Selection[/bold cyan]")
    console.print("[dim]Add caching layer for better performance[/dim]\n")

    cache_catalog = settings.PACKAGE_CATALOG["caching"]
    options = {
        name: f"Packages: {', '.join(pkgs) if pkgs else 'None'}"
        for name, pkgs in cache_catalog.items()
    }

    render_selection_table("Caching Options", options)

    choice = click.prompt(
        "\nSelect caching",
        type=click.IntRange(1, len(options)),
        default=len(options),  # Default to "None"
    )

    return cast(str, list(options.keys())[choice - 1])


def prompt_monitoring_selection(settings: Any) -> str:
    """
    Prompt for monitoring/logging selection.

    Args:
        settings: FastkitConfig instance

    Returns:
        Monitoring type name
    """
    console.print("\n[bold cyan]📊 Monitoring & Logging Selection[/bold cyan]")
    console.print("[dim]Add monitoring and logging capabilities[/dim]\n")

    monitoring_catalog = settings.PACKAGE_CATALOG["monitoring"]
    options = {}

    for name, pkgs in monitoring_catalog.items():
        if name == "None":
            options[name] = "No additional monitoring"
        elif name == "Loguru":
            options[name] = "Enhanced logging with Loguru"
        elif name == "OpenTelemetry":
            options[name] = "Distributed tracing and metrics"
        elif name == "Prometheus":
            options[name] = "Prometheus metrics instrumentation"
        else:
            options[name] = f"Packages: {', '.join(pkgs)}"

    render_selection_table("Monitoring Options", options)

    choice = click.prompt(
        "\nSelect monitoring",
        type=click.IntRange(1, len(options)),
        default=len(options),  # Default to "None"
    )

    return cast(str, list(options.keys())[choice - 1])


def prompt_testing_selection(settings: Any) -> str:
    """
    Prompt for testing framework selection.

    Args:
        settings: FastkitConfig instance

    Returns:
        Testing type name
    """
    console.print("\n[bold cyan]🧪 Testing Framework Selection[/bold cyan]")
    console.print("[dim]Choose testing tools and coverage[/dim]\n")

    testing_catalog = settings.PACKAGE_CATALOG["testing"]
    options = {}

    for name, pkgs in testing_catalog.items():
        if name == "None":
            options[name] = "No testing framework"
        elif name == "Basic":
            options[name] = "pytest + httpx for API testing"
        elif name == "Coverage":
            options[name] = "Basic + code coverage"
        elif name == "Advanced":
            options[name] = "Coverage + faker + factory-boy for fixtures"
        else:
            options[name] = f"Packages: {', '.join(pkgs)}"

    render_selection_table("Testing Options", options)

    choice = click.prompt(
        "\nSelect testing framework",
        type=click.IntRange(1, len(options)),
        default=2,  # Default to "Basic"
    )

    return cast(str, list(options.keys())[choice - 1])


def prompt_utilities_selection(settings: Any) -> List[str]:
    """
    Prompt for utilities selection (multi-select).

    Args:
        settings: FastkitConfig instance

    Returns:
        List of selected utility names
    """
    console.print("\n[bold cyan]🛠️  Additional Utilities[/bold cyan]")
    console.print(
        "[dim]Select additional utilities (comma-separated numbers, e.g., 1,3,4)[/dim]\n"
    )

    utilities_catalog = settings.PACKAGE_CATALOG["utilities"]
    options = []
    descriptions = {}

    for name, pkgs in utilities_catalog.items():
        if name == "None":
            continue
        options.append(name)
        if name == "CORS":
            descriptions[name] = "(Built-in, will configure in settings)"
        elif name == "Rate-Limiting":
            descriptions[name] = "API rate limiting with slowapi"
        elif name == "Pagination":
            descriptions[name] = "Response pagination utilities"
        elif name == "WebSocket":
            descriptions[name] = "(Built-in, will configure routes)"
        else:
            descriptions[name] = f"({', '.join(pkgs)})"

    for i, option in enumerate(options, 1):
        desc = descriptions.get(option, "")
        console.print(f"  [cyan]{i}[/cyan]. {option} {desc}")

    selected_input = console.input(
        "\n[cyan]Your choice (or press Enter to skip):[/cyan] "
    ).strip()

    if not selected_input:
        return []

    try:
        indices = [int(x.strip()) for x in selected_input.split(",") if x.strip()]
        selected = [options[idx - 1] for idx in indices if 1 <= idx <= len(options)]
        return selected
    except (ValueError, IndexError):
        console.print("[yellow]Invalid selection. Skipping utilities.[/yellow]")
        return []


def prompt_deployment_options() -> List[str]:
    """
    Prompt for deployment configuration.

    Returns:
        List of deployment options
    """
    console.print("\n[bold cyan]🚀 Deployment Configuration[/bold cyan]")
    console.print("[dim]Select deployment options (comma-separated numbers)[/dim]\n")

    options = [
        "Docker",
        "docker-compose",
        "None",
    ]

    descriptions = {
        "Docker": "Generate Dockerfile",
        "docker-compose": "Generate docker-compose.yml (includes Docker)",
        "None": "No deployment configuration",
    }

    for i, option in enumerate(options, 1):
        desc = descriptions.get(option, "")
        console.print(f"  [cyan]{i}[/cyan]. {option} - {desc}")

    choice = click.prompt(
        "\nSelect deployment option",
        type=click.IntRange(1, len(options)),
        default=3,  # Default to "None"
    )

    selected = options[choice - 1]

    if selected == "None":
        return []
    elif selected == "docker-compose":
        return ["Docker", "docker-compose"]
    else:
        return [selected]


def prompt_package_manager_selection(settings: Any) -> str:
    """
    Prompt for package manager selection.

    Args:
        settings: FastkitConfig instance

    Returns:
        Package manager name
    """
    console.print("\n[bold cyan]📦 Package Manager Selection[/bold cyan]")
    console.print("[dim]Choose your preferred package manager[/dim]\n")

    options = {}
    for manager, config in settings.PACKAGE_MANAGER_CONFIG.items():
        options[manager] = config["description"]

    render_selection_table("Package Managers", options)

    # Find default index
    default_idx = list(options.keys()).index(settings.DEFAULT_PACKAGE_MANAGER) + 1

    choice = click.prompt(
        "\nSelect package manager",
        type=click.IntRange(1, len(options)),
        default=default_idx,
    )

    return cast(str, list(options.keys())[choice - 1])


def prompt_custom_packages() -> List[str]:
    """
    Prompt for custom package names (manual entry).

    Returns:
        List of custom package names
    """
    console.print("\n[bold cyan]➕ Additional Custom Packages[/bold cyan]")
    console.print(
        "[dim]Enter any additional packages (comma-separated) or press Enter to skip[/dim]\n"
    )

    packages_input = console.input("[cyan]Package names:[/cyan] ").strip()

    if not packages_input:
        return []

    # Split by comma and clean
    packages = [pkg.strip() for pkg in packages_input.split(",") if pkg.strip()]

    return packages


def prompt_additional_features(settings: Any) -> Dict[str, Any]:
    """
    Prompt for all additional features in sequence.

    This is a convenience function that calls all feature prompts.

    Args:
        settings: FastkitConfig instance

    Returns:
        Dictionary with all feature selections
    """
    features: Dict[str, Any] = {}

    # Database
    features["database"] = prompt_database_selection(settings)

    # Authentication
    features["authentication"] = prompt_authentication_selection(settings)

    # Async tasks
    features["async_tasks"] = prompt_async_tasks_selection(settings)

    # Caching
    features["caching"] = prompt_caching_selection(settings)

    # Monitoring
    features["monitoring"] = prompt_monitoring_selection(settings)

    # Testing
    features["testing"] = prompt_testing_selection(settings)

    # Utilities
    features["utilities"] = prompt_utilities_selection(settings)

    # Deployment
    features["deployment"] = prompt_deployment_options()

    # Package manager
    features["package_manager"] = prompt_package_manager_selection(settings)

    # Custom packages
    features["custom_packages"] = prompt_custom_packages()

    return features
