# TODO : make logic with click(cli operation) & rich(decorate console outputs and indicate manuals)
# --------------------------------------------------------------------------
# The Module defines main and core CLI operations for FastAPI-fastkit.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import click
import subprocess
import shutil

from typing import Union

from logging import getLogger

from click.core import BaseCommand, Context

from rich import print
from rich.panel import Panel

from . import __version__
from .backend import validate_email, inject_project_metadata, read_template_stack
from fastapi_fastkit.utils.logging import setup_logging
from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.core.exceptions import CLIExceptions
from fastapi_fastkit.utils.transducer import copy_and_convert_template
from fastapi_fastkit.utils.inspector import delete_project


logger = getLogger(__name__)


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.version_option(__version__, prog_name="fastapi-fastkit")
@click.pass_context
def fastkit_cli(ctx: Context, debug: bool) -> Union["BaseCommand", None]:
    """
    main FastAPI-fastkit CLI operation group

    :param ctx: context of passing configurations (NOT specify it at CLI)
    :type ctx: <Object click.Context>
    :param debug: parameter from CLI
    :return: None(will be wrapped with click.core.BaseCommand via @click decorator)
    """
    settings = FastkitConfig()

    ctx.ensure_object(dict)

    if debug:
        warning_panel = Panel(
            "running at debugging mode!!",
            title="❗️ Warning ❗",
            style="yellow",
            highlight=True,
        )
        click.echo(print(warning_panel))
        settings.set_debug_mode()

    ctx.obj["settings"] = settings

    setup_logging(settings=settings)

    return None


@fastkit_cli.command()
@click.pass_context
def echo(ctx: Context) -> None:
    """
    About FastAPI-fastkit

    :param ctx: context of passing configurations (NOT specify it at CLI)
    :type ctx: <Object click.Context>
    :return: None
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
def list_templates() -> None:
    """
    Display the list of available templates.

    :return: None
    """
    settings = FastkitConfig()
    template_dir = settings.FASTKIT_TEMPLATE_ROOT

    if not os.path.exists(template_dir):
        click.echo("Template directory not found.")
        return

    templates = [
        d
        for d in os.listdir(template_dir)
        if os.path.isdir(os.path.join(template_dir, d))
    ]

    if not templates:
        click.echo("No available templates.")
        return

    click.echo("\nAvailable templates:")
    for template in templates:
        template_path = os.path.join(template_dir, template)
        readme_path = os.path.join(template_path, "README.md-tpl")

        description = "No description"
        if os.path.exists(readme_path):
            with open(readme_path, "r") as f:
                first_line = f.readline().strip()
                if first_line.startswith("# "):
                    description = first_line[2:]

        click.echo(f"- {template}: {description}")


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
@click.pass_context
def startup(
    ctx: Context,
    template: str,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
) -> None:
    """
    Create a new FastAPI project from templates and inject metadata.

    :param ctx: Click context object
    :param template: Template name
    :param project_name: Project name for the new project
    :param author: Author name
    :param author_email: Author email
    :param description: Project description
    :return: None
    """
    settings = ctx.obj["settings"]

    template_dir = settings.FASTKIT_TEMPLATE_ROOT
    click.echo(f"Deploying FastAPI project using '{template}' template")
    target_template = os.path.join(template_dir, template)
    print(f"Template path: {target_template}")

    if not os.path.exists(target_template):
        raise CLIExceptions(
            f"Error: Template '{template}' does not exist in '{template_dir}'."
        )
    click.echo(f"\nProject Name: {project_name}")
    click.echo(f"Author: {author}")
    click.echo(f"Author Email: {author_email}")
    click.echo(f"Description: {description}")
    read_template_stack()
    # click.echo("Project Stack: [FastAPI, Uvicorn, SQLAlchemy, Docker (optional)]")  # TODO : impl this?

    confirm = click.confirm(
        "\nDo you want to proceed with project creation?", default=False
    )
    if not confirm:
        click.echo("Project creation aborted!")
        return

    try:
        user_local = settings.USER_WORKSPACE
        project_dir = os.path.join(user_local, project_name)

        click.echo(f"FastAPI template project will deploy at '{user_local}'")

        copy_and_convert_template(target_template, user_local, project_name)

        inject_project_metadata(
            project_dir, project_name, author, author_email, description
        )

        click.echo(
            f"FastAPI project '{project_name}' from '{template}' has been created and saved to {user_local}!"
        )
    except Exception as e:
        click.echo(f"Error during project creation: {e}")


@fastkit_cli.command(context_settings={"ignore_unknown_options": True})
@click.option(
    "--project-name",
    prompt="Enter project name",
    help="Name of the new FastAPI project",
)
@click.option(
    "--stack",
    type=click.Choice(["minimal", "standard", "full"]),
    prompt="Select stack",
    help="Project stack configuration",
)
def startproject(project_name: str, stack: str) -> None:
    """
    Start a new FastAPI project.
    Dependencies will be automatically installed based on the selected stack.

    :param project_name: Project name
    :param stack: Project stack configuration
    :return: None
    """
    settings = FastkitConfig()
    project_dir = os.path.join(settings.USER_WORKSPACE, project_name)

    if os.path.exists(project_dir):
        click.echo(f"Error: Project '{project_name}' already exists.")
        return

    try:
        os.makedirs(project_dir)

        dependencies = {
            "minimal": ["fastapi", "uvicorn"],
            "standard": ["fastapi", "uvicorn", "sqlalchemy", "alembic", "pytest"],
            "full": [
                "fastapi",
                "uvicorn",
                "sqlalchemy",
                "alembic",
                "pytest",
                "redis",
                "celery",
                "docker-compose",
            ],
        }

        with open(os.path.join(project_dir, "requirements.txt"), "w") as f:
            for dep in dependencies[stack]:
                f.write(f"{dep}\n")

        click.echo("Creating virtual environment and installing dependencies...")
        subprocess.run(["python", "-m", "venv", os.path.join(project_dir, "venv")])
        subprocess.run(["pip", "install", "-r", "requirements.txt"], cwd=project_dir)

        click.echo(f"Project '{project_name}' has been created successfully!")

    except Exception as e:
        click.echo(f"Error during project creation: {e}")
        shutil.rmtree(project_dir, ignore_errors=True)


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


@fastkit_cli.command()
@click.argument("project_name")
@click.pass_context
def deleteproject(ctx: Context, project_name: str) -> None:
    """
    Delete a FastAPI project.

    :param ctx: Click context object
    :param project_name: Project name
    :return: None
    """
    settings = ctx.obj["settings"]
    user_local = settings.USER_WORKSPACE
    project_dir = os.path.join(user_local, project_name)

    if not os.path.exists(project_dir):
        click.echo(f"Error: Project '{project_name}' does not exist in '{user_local}'.")
        return

    if not is_fastkit_project(project_dir):
        click.echo(f"Error: '{project_name}' is not a FastAPI-fastkit project.")
        return

    confirm = click.confirm(
        f"\nDo you want to delete project '{project_name}' at '{project_dir}'?",
        default=False,
    )
    if not confirm:
        click.echo("Project deletion cancelled!")
        return

    try:
        delete_project(project_dir)
        click.echo(
            f"Project '{project_name}' has been successfully deleted from '{user_local}'."
        )
    except Exception as e:
        click.echo(f"Error during project deletion: {e}")


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
    [TODO] Alternative Point : using FastAPI-fastkit's 'fastapi dev' command

    :param ctx: Click context object
    :param host: Host address to bind the server to
    :param port: Port number to bind the server to
    :param reload: Enable or disable auto-reload
    :return: None
    """
    settings = ctx.obj["settings"]
    project_dir = settings.USER_WORKSPACE

    app_path = os.path.join(project_dir, "main.py")
    if not os.path.exists(app_path):
        click.echo(f"Error: Could not find 'main.py' in '{project_dir}'.")
        return

    command = [
        "uvicorn",
        "main:app",
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
        click.echo(f"Starting FastAPI server at {host}:{port}...")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: Failed to start FastAPI server.\n{e}")
