# --------------------------------------------------------------------------
# The Module defines backend operations for FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import re
import os
import click

from typing import Any, Union

from logging import getLogger

from click.core import Context

from fastapi_fastkit.core.exceptions import TemplateExceptions


logger = getLogger(__name__)

REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"


def validate_email(ctx: Context, param: Any, value: Any) -> Any:
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


def inject_project_metadata(
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


# TODO : modify this function
# def read_template_stack() -> Union[list, None]:
#     pass
