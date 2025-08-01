# --------------------------------------------------------------------------
# The Module defines main and core CLI operations for FastAPI-fastkit.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import atexit
import os
import shutil
import subprocess
import sys
from typing import Union

import click
from click.core import BaseCommand, Context
from rich import print
from rich.panel import Panel

from fastapi_fastkit.backend.main import (
    add_new_route,
    create_venv_with_manager,
    find_template_core_modules,
    generate_dependency_file_with_manager,
    inject_project_metadata,
    install_dependencies_with_manager,
    read_template_stack,
)
from fastapi_fastkit.backend.transducer import copy_and_convert_template
from fastapi_fastkit.core.exceptions import CLIExceptions
from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.utils.logging import get_logger, setup_logging
from fastapi_fastkit.utils.main import (
    create_info_table,
    is_fastkit_project,
    print_error,
    print_info,
    print_success,
    print_warning,
    validate_email,
)

from . import __version__, console


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.version_option(__version__, prog_name="fastapi-fastkit")
@click.pass_context
def fastkit_cli(ctx: Context, debug: bool) -> Union["BaseCommand", None]:
    """
    main FastAPI-fastkit CLI operation group
    """
    settings = FastkitConfig()
    ctx.ensure_object(dict)

    if debug:
        print_warning("running at debugging mode!!")
        settings.set_debug_mode()

    ctx.obj["settings"] = settings

    # Setup logging and get debug capture if debug mode is enabled
    debug_capture = setup_logging(settings=settings)
    ctx.obj["debug_capture"] = debug_capture

    # If debug mode is enabled, start capturing output
    if debug_capture:
        debug_capture.__enter__()
        # Log CLI invocation
        logger = get_logger()
        logger.info(f"CLI invoked with debug mode: {' '.join(sys.argv)}")

        # Register cleanup function for when the CLI exits
        def cleanup_debug_capture() -> None:
            try:
                debug_capture.__exit__(None, None, None)
                logger.info("FastAPI-fastkit CLI session ended")
            except Exception:
                pass  # Fail silently during cleanup

        atexit.register(cleanup_debug_capture)

    return None


@fastkit_cli.command()
@click.pass_context
def echo(ctx: Context) -> None:
    """
    About FastAPI-fastkit
    """
    fastkit_info = f"""
    ⚡️ FastAPI fastkit - fastest [bold]FastAPI[/bold] initializer. ⚡️

    Deploy FastAPI app foundation instantly at your local!

    ---
    - Project Maintainer : [link=mailto:bbbong9@gmail.com]bnbong(JunHyeok Lee)[/link]
    - Current Version : {__version__}
    - Github : [link]https://github.com/bnbong/FastAPI-fastkit[/link]
    """
    settings = ctx.obj["settings"]
    description_panel = Panel(fastkit_info, title="About FastAPI-fastkit")
    click.echo(print(description_panel))

    if settings.DEBUG_MODE:
        debug_output = f"FASTKIT_PROJECT_ROOT: {settings.FASTKIT_PROJECT_ROOT}\nUSER_WORKSPACE: {settings.USER_WORKSPACE}"

        click.echo(debug_output)


@fastkit_cli.command()
@click.pass_context
def list_templates(ctx: Context) -> None:
    """
    Display the list of available templates.
    """
    settings = ctx.obj["settings"]
    template_dir = settings.FASTKIT_TEMPLATE_ROOT

    if not os.path.exists(template_dir):
        print_error("Template directory not found.")
        return

    excluded_dirs = ["__pycache__", "modules"]
    templates = [
        d
        for d in os.listdir(template_dir)
        if os.path.isdir(os.path.join(template_dir, d)) and d not in excluded_dirs
    ]

    if not templates:
        print_warning("No available templates.")
        return

    table = create_info_table("Available Templates")

    for template in templates:
        template_path = os.path.join(template_dir, template)
        readme_path = os.path.join(template_path, "README.md-tpl")

        description = "No description"
        if os.path.exists(readme_path):
            with open(readme_path, "r") as f:
                first_line = f.readline().strip()
                if first_line.startswith("# "):
                    description = first_line[2:]

        table.add_row(template, description)

    console.print(table)


@fastkit_cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("template", default="fastapi-default")
@click.option(
    "--project-name",
    prompt="Enter the project name",
    help="The name of the new FastAPI project.",
)
@click.option(
    "--author", prompt="Enter the author name", help="The name of the project author."
)
@click.option(
    "--author-email",
    prompt="Enter the author email",
    help="The email of the project author.",
    type=str,
    callback=validate_email,
)
@click.option(
    "--description",
    prompt="Enter the project description",
    help="The description of the new FastAPI project.",
)
@click.option(
    "--package-manager",
    help="Package manager to use for the project.",
    type=click.Choice(["pip", "uv", "pdm", "poetry"]),
    default=None,
)
@click.pass_context
def startdemo(
    ctx: Context,
    template: str,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
    package_manager: str,
) -> None:
    """
    Create a new FastAPI project from templates and inject metadata.
    """
    settings = ctx.obj["settings"]

    template_dir = settings.FASTKIT_TEMPLATE_ROOT
    click.echo(f"Deploying FastAPI project using '{template}' template")
    target_template = os.path.join(template_dir, template)

    if settings.DEBUG_MODE:
        logger = get_logger()
        logger.info(f"Template path: {target_template}")

    click.echo(f"Template path: {target_template}")

    if not os.path.exists(target_template):
        print_error(f"Template '{template}' does not exist in '{template_dir}'.")
        raise CLIExceptions(
            f"Template '{template}' does not exist in '{template_dir}'."
        )
    table = create_info_table(
        "Project Information",
        {
            "Project Name": project_name,
            "Author": author,
            "Author Email": author_email,
            "Description": description,
        },
    )

    console.print("\n")
    console.print(table)

    template_deps = read_template_stack(target_template)
    if template_deps:
        deps_table = create_info_table(
            "Template Dependencies",
            {f"Dependency {i+1}": dep for i, dep in enumerate(template_deps)},
        )
        console.print("\n")
        console.print(deps_table)

    # Package manager selection
    if not package_manager:
        console.print("\n[bold]Available Package Managers:[/bold]")
        package_manager_table = create_info_table(
            "Package Managers",
            {
                f"{manager.upper()}": config["description"]
                for manager, config in settings.PACKAGE_MANAGER_CONFIG.items()
            },
        )
        console.print(package_manager_table)
        console.print("\n")

        package_manager = click.prompt(
            "Select package manager",
            type=click.Choice(settings.SUPPORTED_PACKAGE_MANAGERS),
            default=settings.DEFAULT_PACKAGE_MANAGER,
            show_choices=True,
            show_default=True,
        )

    confirm = click.confirm(
        "\nDo you want to proceed with project creation?", default=False
    )
    if not confirm:
        print_error("Project creation aborted!")
        return

    try:
        user_local = settings.USER_WORKSPACE
        project_dir = os.path.join(user_local, project_name)

        click.echo(f"FastAPI template project will deploy at '{user_local}'")

        copy_and_convert_template(target_template, user_local, project_name)

        inject_project_metadata(
            project_dir, project_name, author, author_email, description
        )

        # Create virtual environment and install dependencies with selected package manager
        venv_path = create_venv_with_manager(project_dir, package_manager)
        install_dependencies_with_manager(project_dir, venv_path, package_manager)

        print_success(
            f"FastAPI project '{project_name}' from '{template}' has been created and saved to {user_local}!"
        )

    except Exception as e:
        if settings.DEBUG_MODE:
            logger = get_logger()
            logger.exception(f"Error during project creation in startdemo: {str(e)}")
        print_error(f"Error during project creation: {str(e)}")


@fastkit_cli.command(context_settings={"ignore_unknown_options": True})
@click.option(
    "--project-name",
    prompt="Enter the project name",
    help="The name of the new FastAPI project.",
)
@click.option(
    "--author", prompt="Enter the author name", help="The name of the project author."
)
@click.option(
    "--author-email",
    prompt="Enter the author email",
    help="The email of the project author.",
    type=str,
    callback=validate_email,
)
@click.option(
    "--description",
    prompt="Enter the project description",
    help="The description of the new FastAPI project.",
)
@click.option(
    "--package-manager",
    help="Package manager to use for the project.",
    type=click.Choice(["pip", "uv", "pdm", "poetry"]),
    default=None,
)
@click.pass_context
def init(
    ctx: Context,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
    package_manager: str,
) -> None:
    """
    Start a empty FastAPI project setup.
    This command will automatically create a new FastAPI project directory and a python virtual environment.
    Dependencies will be automatically installed based on the selected stack at venv.
    Project metadata will be injected to the project files.
    """
    settings = ctx.obj["settings"]
    project_dir = os.path.join(settings.USER_WORKSPACE, project_name)

    if os.path.exists(project_dir):
        print_error(f"Error: Project '{project_name}' already exists.")
        return

    # Display project information
    project_info_table = create_info_table(
        "Project Information",
        {
            "Project Name": project_name,
            "Author": author,
            "Author Email": author_email,
            "Description": description,
        },
    )
    console.print("\n")
    console.print(project_info_table)

    # Display available stacks
    console.print("\n[bold]Available Stacks and Dependencies:[/bold]")

    for stack_name, deps in settings.PROJECT_STACKS.items():
        table = create_info_table(
            f"{stack_name.upper()} Stack",
            {f"Dependency {i+1}": dep for i, dep in enumerate(deps)},
        )
        console.print(table)
        console.print("\n")

    stack = click.prompt(
        "Select stack",
        type=click.Choice(list(settings.PROJECT_STACKS.keys())),
        show_choices=True,
    )

    # Package manager selection
    if not package_manager:
        console.print("\n[bold]Available Package Managers:[/bold]")
        package_manager_table = create_info_table(
            "Package Managers",
            {
                f"{manager.upper()}": config["description"]
                for manager, config in settings.PACKAGE_MANAGER_CONFIG.items()
            },
        )
        console.print(package_manager_table)
        console.print("\n")

        package_manager = click.prompt(
            "Select package manager",
            type=click.Choice(settings.SUPPORTED_PACKAGE_MANAGERS),
            default=settings.DEFAULT_PACKAGE_MANAGER,
            show_choices=True,
            show_default=True,
        )

    template = "fastapi-empty"
    template_dir = settings.FASTKIT_TEMPLATE_ROOT
    target_template = os.path.join(template_dir, template)

    if not os.path.exists(target_template):
        print_error(f"Template '{template}' does not exist in '{template_dir}'.")
        raise CLIExceptions(
            f"Template '{template}' does not exist in '{template_dir}'."
        )

    confirm = click.confirm(
        "\nDo you want to proceed with project creation?", default=False
    )
    if not confirm:
        print_error("Project creation aborted!")
        return

    try:
        user_local = settings.USER_WORKSPACE
        project_dir = os.path.join(user_local, project_name)

        click.echo(f"FastAPI project will deploy at '{user_local}'")

        copy_and_convert_template(target_template, user_local, project_name)

        inject_project_metadata(
            project_dir, project_name, author, author_email, description
        )

        deps_table = create_info_table(
            f"Creating Project: {project_name}", {"Component": "Collected"}
        )

        # Generate dependency file using selected package manager
        dependencies = settings.PROJECT_STACKS[stack]
        generate_dependency_file_with_manager(
            project_dir,
            dependencies,
            package_manager,
            project_name,
            author,
            author_email,
            description,
        )

        for dep in dependencies:
            deps_table.add_row(dep, "✓")

        console.print(deps_table)

        # Create virtual environment and install dependencies with selected package manager
        venv_path = create_venv_with_manager(project_dir, package_manager)
        install_dependencies_with_manager(project_dir, venv_path, package_manager)

        print_success(
            f"FastAPI project '{project_name}' has been created successfully and saved to {user_local}!"
        )

        print_info(
            "To start your project, run 'fastkit runserver' at newly created FastAPI project directory"
        )

    except Exception as e:
        if settings.DEBUG_MODE:
            logger = get_logger()
            logger.exception(f"Error during project creation in init: {str(e)}")
        print_error(f"Error during project creation: {str(e)}")
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir, ignore_errors=True)


@fastkit_cli.command()
@click.argument("project_name")
@click.argument("route_name")
@click.pass_context
def addroute(ctx: Context, project_name: str, route_name: str) -> None:
    """
    Add a new route to the FastAPI project.
    """
    settings = ctx.obj["settings"]
    user_local = settings.USER_WORKSPACE
    project_dir = os.path.join(user_local, project_name)

    # Check if project exists
    if not os.path.exists(project_dir):
        print_error(f"Project '{project_name}' does not exist in '{user_local}'.")
        return

    # Verify it's a fastkit project
    if not is_fastkit_project(project_dir):
        print_error(f"'{project_name}' is not a FastAPI-fastkit project.")
        return

    # Validate route name
    if not route_name.isidentifier():
        print_error(f"Route name '{route_name}' is not a valid Python identifier.")
        return

    # Route name shouldn't match reserved keywords
    import keyword

    if keyword.iskeyword(route_name):
        print_error(
            f"Route name '{route_name}' is a Python keyword and cannot be used."
        )
        return

    try:
        # Show information about the operation
        table = create_info_table(
            "Adding New Route",
            {
                "Project": project_name,
                "Route Name": route_name,
                "Target Directory": project_dir,
            },
        )
        console.print(table)

        # Confirm before proceeding
        confirm = click.confirm(
            f"\nDo you want to add route '{route_name}' to project '{project_name}'?",
            default=True,
        )
        if not confirm:
            print_error("Operation cancelled!")
            return

        # Add the new route
        add_new_route(project_dir, route_name)

        print_success(
            f"Successfully added new route '{route_name}' to project `{project_name}`"
        )

    except Exception as e:
        logger = get_logger()
        logger.exception(f"Error during route addition: {str(e)}")
        print_error(f"Error during route addition: {str(e)}")


@fastkit_cli.command()
@click.argument("project_name")
@click.pass_context
def deleteproject(ctx: Context, project_name: str) -> None:
    """
    Delete a FastAPI project.
    """
    settings = ctx.obj["settings"]
    user_local = settings.USER_WORKSPACE
    project_dir = os.path.join(user_local, project_name)

    if not os.path.exists(project_dir):
        print_error(f"Project '{project_name}' does not exist in '{user_local}'.")
        return

    if not is_fastkit_project(project_dir):
        print_error(f"'{project_name}' is not a FastAPI-fastkit project.")
        return

    confirm = click.confirm(
        f"\nDo you want to delete project '{project_name}' at '{project_dir}'?",
        default=False,
    )
    if not confirm:
        print_error("Project deletion cancelled!")
        return

    try:
        shutil.rmtree(project_dir)
        print_success(f"Project '{project_name}' has been deleted successfully!")

    except Exception as e:
        logger = get_logger()
        logger.exception(f"Error during project deletion: {e}")
        print_error(f"Error during project deletion: {e}")


@fastkit_cli.command()
@click.option(
    "--host",
    default="127.0.0.1",
    show_default=True,
    help="Host to bind the server",
)
@click.option(
    "--port",
    default=8000,
    show_default=True,
    help="Port to bind the server",
)
@click.option(
    "--reload/--no-reload",
    default=True,
    show_default=True,
    help="Enable/disable auto-reload on code changes",
)
@click.option(
    "--workers",
    default=1,
    show_default=True,
    help="Number of worker processes",
)
@click.pass_context
def runserver(
    ctx: Context,
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    workers: int = 1,
) -> None:
    """
    Run the FastAPI server for the current project.
    """
    settings = ctx.obj["settings"]
    project_dir = settings.USER_WORKSPACE

    # Check for virtual environment
    venv_path = os.path.join(project_dir, ".venv")
    if not os.path.exists(venv_path) or not os.path.isdir(venv_path):
        print_error(
            "Virtual environment not found. Is this a project deployed with Fastkit?"
        )
        confirm = click.confirm(
            "Do you want to continue with system Python?", default=False
        )
        if not confirm:
            return
        venv_python = None
    else:
        if os.name == "nt":  # Windows
            venv_python = os.path.join(venv_path, "Scripts", "python.exe")
        else:  # Unix/Linux/Mac
            venv_python = os.path.join(venv_path, "bin", "python")

        if not os.path.exists(venv_python):
            print_error(
                f"Python interpreter not found in virtual environment: {venv_python}"
            )
            confirm = click.confirm(
                "Do you want to continue with system Python?", default=False
            )
            if not confirm:
                return
            venv_python = None

    core_modules = find_template_core_modules(project_dir)
    if not core_modules["main"]:
        print_error(f"Could not find 'main.py' in '{project_dir}'.")
        return

    main_path = core_modules["main"]
    if "src/" in main_path:
        app_module = "src.main:app"
    else:
        app_module = "main:app"

    if venv_python:
        print_info(f"Using Python from virtual environment: {venv_python}")
        command = [
            venv_python,
            "-m",
            "uvicorn",
            app_module,
            "--host",
            host,
            "--port",
            str(port),
            "--workers",
            str(workers),
        ]
    else:
        command = [
            "uvicorn",
            app_module,
            "--host",
            host,
            "--port",
            str(port),
            "--workers",
            str(workers),
        ]

    if reload:
        command.append("--reload")

    try:
        print_success(f"Starting FastAPI server at {host}:{port}...")

        # Set up environment variables for the subprocess
        env = os.environ.copy()
        if venv_python:
            python_path = os.path.dirname(os.path.dirname(venv_python))
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = f"{python_path}:{env['PYTHONPATH']}"
            else:
                env["PYTHONPATH"] = python_path

        # Run the server with the configured environment
        subprocess.run(command, check=True, env=env)
    except subprocess.CalledProcessError as e:
        logger = get_logger()
        logger.exception(f"Failed to start FastAPI server: {e}")
        print_error(f"Failed to start FastAPI server.\n{e}")
    except FileNotFoundError as e:
        logger = get_logger()
        logger.exception(f"FileNotFoundError when starting server: {e}")
        if venv_python:
            print_error(
                f"Failed to run Python from the virtual environment. Make sure uvicorn is installed in the project's virtual environment."
            )
        else:
            print_error(
                f"uvicorn not found. Make sure it's installed in your system Python."
            )
