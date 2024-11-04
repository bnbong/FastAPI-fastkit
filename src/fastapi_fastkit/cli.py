# TODO : make logic with click(cli operation) & rich(decorate console outputs and indicate manuals)
# --------------------------------------------------------------------------
# The Module defines main and core CLI operations for FastAPI-fastkit.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import click

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
def list() -> None:
    # TODO : impl this
    """
    Get available templates list.
    :return: None
    """
    pass


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
def startproject() -> None:
    # TODO : impl this, add a stack selecting process?
    """
    Start a empty FastAPI project.
    :return:
    """
    pass


@fastkit_cli.command()
@click.argument("project_name")
@click.pass_context
def deleteproject(ctx: Context, project_name: str) -> None:
    # TODO : add checking step - if target project is not from fastkit, discard the attempt.
    settings = ctx.obj["settings"]

    user_local = settings.USER_WORKSPACE
    project_dir = os.path.join(user_local, project_name)

    if not os.path.exists(project_dir):
        click.echo(f"Error: Project '{project_name}' does not exist at '{user_local}'.")
        return

    confirm = click.confirm(
        f"\nAre you sure you want to delete the project '{project_name}' at '{project_dir}'?",
        default=False,
    )
    if not confirm:
        click.echo("Project deletion aborted!")
        return

    try:
        # TODO : adjust this
        delete_project(project_dir)
        click.echo(
            f"Project '{project_name}' has been successfully deleted from '{user_local}'."
        )
    except Exception as e:
        click.echo(f"Error during project deletion: {e}")


@fastkit_cli.command()
@click.pass_context
def runserver(ctx: Context) -> None:
    """
    Run FastAPI template server at CLI

    :param ctx: context of passing configurations (NOT specify it at CLI)
    :type ctx: <Object click.Context>
    :return: None
    """
    # TODO : implement this using fastapi-cli?
    pass
