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

from click.core import BaseCommand

from rich import print
from rich.panel import Panel

from . import __version__
from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.core.exceptions import CLIExceptions, TemplateExceptions
from fastapi_fastkit.utils.transducer import copy_and_convert_template


logger = getLogger(__name__)


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def fastkit_cli(ctx, debug) -> Union["BaseCommand", None]:
    """
    main FastAPI-fastkit CLI operation group

    :param ctx: context of passing configurations (NOT specify it at CLI)
    :type ctx: <Object click.Context>
    :param debug: parameter from CLI
    :return: None(will be wrapped with click.core.BaseCommand via @click decorator)
    """
    ctx.ensure_object(dict)

    ctx.obj['DEBUG'] = debug

    return


@fastkit_cli.command(context_settings={"ignore_unknown_options": True})
@click.argument("template")
@click.pass_context
def startproject(ctx, template: str) -> None:
    """
    Create a new FastAPI project from templates.

    :param ctx: context of passing configurations (NOT specify it at CLI)
    :type ctx: <Object click.Context>
    :param template: name of the template to deploy
    :type template: str
    :return: None
    """
    if ctx.obj['DEBUG']:
        click.echo(print('[yellow]runs at debugging mode!![/yellow]'))
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
@click.pass_context
def echo(ctx) -> None:
    """
    About FastAPI-fastkit

    :param ctx: context of passing configurations (NOT specify it at CLI)
    :type ctx: <Object click.Context>
    :return: None
    """
    if ctx.obj['DEBUG']:
        click.echo(print('[yellow]runs at debugging mode!![/yellow]'))

    fastkit_info = f"""
    ⚡️ FastAPI fastkit - fastest [bold]FastAPI[/bold] initializer. ⚡️
    
    Deploy FastAPI app foundation instantly at your local!
    
    ---
    - Project Maintainer : [link=mailto:bbbong9@gmail.com]bnbong(JunHyeok Lee)[/link]
    - Current Version : {__version__}
    - Github : [link]https://github.com/bnbong/FastAPI-fastkit[/link]
    """
    description_panel = Panel(fastkit_info, title="About FastAPI-fastkit")
    click.echo(print(description_panel))


@fastkit_cli.command()
@click.pass_context
def runserver(ctx) -> None:
    """
    Run FastAPI template server at CLI

    :param ctx: context of passing configurations (NOT specify it at CLI)
    :type ctx: <Object click.Context>
    :return: None
    """
    if ctx.obj['DEBUG']:
        click.echo(print('[yellow]runs at debugging mode!![/yellow]'))
    # TODO : using fastapi-cli?
    pass
