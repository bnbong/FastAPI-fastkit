# TODO : make logic with click(cli operation) & rich(decorate console outputs and indicate manuals)
# --------------------------------------------------------------------------
# The Module defines main and core CLI operations for FastAPI-fastkit.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import re
import os
import click

from typing import Union

from logging import getLogger

from click.core import BaseCommand, Context

from rich import print
from rich.panel import Panel

from . import __version__
from fastapi_fastkit.utils.logging import setup_logging
from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.core.exceptions import CLIExceptions, TemplateExceptions
from fastapi_fastkit.utils.transducer import copy_and_convert_template


logger = getLogger(__name__)


# --------------------------------------------------------------------------
# Backend operators
# --------------------------------------------------------------------------
REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"


def validate_email(ctx, param, value):
    """
    Check if the provided email is in a valid format.
    This will recursively loop until a valid email input entry is given.

    :param ctx: context of passing configurations (NOT specify it at CLI)
    :type ctx: <Object click.Context>
    :param param: parameters from CLI
    :param value: values from CLI
    :return:
    """
    try:
        if not re.match(REGEX, value):
            raise ValueError(value)
        else:
            return value
    except ValueError as e:
        click.echo("Incorrect email address given: {}".format(e))
        value = click.prompt(param.prompt)
        return validate_email(ctx, param, value)


def _inject_project_metadata(
    target_dir: str,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
) -> None:
    """
    Inject metadata into the main.py and setup.py files.

    :param target_dir: Directory for the new project to deploy
    :param project_name: new project name
    :param author: cli username
    :param author_email: cli user email
    :param description: new project description
    """
    main_py_path = os.path.join(target_dir, "main.py")
    setup_py_path = os.path.join(target_dir, "setup.py")

    try:
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
        click.echo(e)
        raise TemplateExceptions("ERROR : Having some errors with injecting metadata")


def _print_version(ctx: Context, value: click.Option, *args, **kwargs) -> None:
    # TODO : apply this at fastapi-cli group
    """
    print current version of fastapi-fastkit

    :param ctx: context of passing configurations (NOT specify it at CLI)
    :type ctx: <Object click.Context>
    """
    if value:
        version_info = f"fastapi-fastkit version {__version__}"
        click.echo(print(version_info))
        ctx.exit()


# --------------------------------------------------------------------------
# Click operator methods
# --------------------------------------------------------------------------
@click.group()
@click.option("--debug/--no-debug", default=False)
# @click.option('--version', callback=_print_version,
#               expose_value=False)
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

    return


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
def startproject(
    ctx: Context,
    template: str,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
) -> None:
    # TODO : add a feature - name project folder name to project_name
    """
    Create a new FastAPI project from templates and inject metadata.

    :param ctx: Click context object
    :param template: Template name
    :param project_name: Project name for the new project
    :param author: Author name
    :param author_email: Author email
    :param description: Project description
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
    # TODO : add confirm step : checking template stack & name & metadata, confirm it y/n
    # click.echo("Project Stack: [FastAPI, Uvicorn, SQLAlchemy, Docker (optional)]")

    confirm = click.confirm(
        "\nDo you want to proceed with project creation?", default=False
    )
    if not confirm:
        click.echo("Project creation aborted!")
        return

    try:
        user_local = settings.USER_WORKSPACE
        click.echo(f"FastAPI template project will deploy at '{user_local}'")

        click.echo(f"Project Name: {project_name}")

        confirm = click.confirm(
            "\nDo you want to proceed with project creation?", default=False
        )
        if not confirm:
            click.echo("Project creation aborted!")
            return

        copy_and_convert_template(target_template, user_local)

        _new_user_local = os.path.join(user_local, template)

        _inject_project_metadata(
            _new_user_local, project_name, author, author_email, description
        )

        click.echo(
            f"FastAPI project '{project_name}' from '{template}' has been created and saved to {user_local}!"
        )
    except Exception as e:
        click.echo(f"Error during project creation: {e}")


@fastkit_cli.command()
@click.pass_context
def deleteproject(ctx: Context) -> None:
    # TODO : implement this
    pass


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
