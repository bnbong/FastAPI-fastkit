# TODO : add inspect operation target template is valid FastAPI application.
# --------------------------------------------------------------------------
# The Module inspect FastAPI template is appropriate
#
# This module will be read by Github Action when contributor
#   makes a PR of adding new FastAPI template.
#
# @author bnbong
# --------------------------------------------------------------------------
import shutil


def delete_project(project_dir: str) -> None:
    # TODO : add checking step -> preventing 'template' folder deletion.
    shutil.rmtree(project_dir)
