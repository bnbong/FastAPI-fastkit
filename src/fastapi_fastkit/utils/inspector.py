# TODO : add inspect operation target template is valid FastAPI application.
# --------------------------------------------------------------------------
# The Module inspect FastAPI template is appropriate
#
# @author bnbong
# --------------------------------------------------------------------------
import shutil


def delete_project(project_dir: str) -> None:
    # TODO : add checking step -> preventing 'template' folder deletion.
    shutil.rmtree(project_dir)
