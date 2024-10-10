# TODO : make logic with click(cli operation) & rich(decorate console outputs and indicate manuals)
# --------------------------------------------------------------------------
# The Module defines main and core CLI operations for FastAPI-fastkit.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import click

from rich import print

from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.core.exceptions import CLIExceptions, TemplateExceptions
from fastapi_fastkit.utils.transducer import copy_and_convert_template


@click.group()
def fastkit_cli():
    """main FastAPI-fastkit CLI operation group"""
    pass


@fastkit_cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("template")
def startproject(template: str) -> None:
    """Create a new FastAPI project from templates."""
    template_dir = FastkitConfig.FASTKIT_TEMPLATE_ROOT
    target_template = os.path.join(template_dir, template)
    print(target_template)

    if not os.path.exists(target_template):
        raise CLIExceptions(
            f"Error: Template '{template}' does not exist in '{template_dir}'."
        )

    # TODO : add step -> after checking template, inspect target template is valid FastAPI application.

    try:
        user_local = FastkitConfig.USER_WORKSPACE
        click.echo(f"FastAPI template project will deploy at '{user_local}'")

        copy_and_convert_template(target_template, user_local)

        click.echo(
            f"FastAPI project from '{template}' has been created and saved to {user_local}!"
        )
    except Exception as e:
        click.echo(f"Error during project creation: {e}")


@fastkit_cli.command()
def echo() -> None:
    click.echo("Hello World!")
