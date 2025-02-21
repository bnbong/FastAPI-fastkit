# --------------------------------------------------------------------------
# The Module defines backend operations for FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import subprocess

from fastapi_fastkit import console
from fastapi_fastkit.core.exceptions import BackendExceptions, TemplateExceptions
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.main import print_error, print_info, print_success


def find_template_core_modules(project_dir: str) -> dict[str, str]:
    """
    Find core module files in the template project structure.
    Returns a dictionary with paths to main.py, setup.py, and config files.
    """
    core_modules = {"main": "", "setup": "", "config": ""}
    template_config = settings.TEMPLATE_PATHS["config"]

    # Find main.py
    for path in settings.TEMPLATE_PATHS["main"]:
        full_path = os.path.join(project_dir, path)
        if os.path.exists(full_path):
            core_modules["main"] = full_path
            break

    # Find setup.py
    for path in settings.TEMPLATE_PATHS["setup"]:
        full_path = os.path.join(project_dir, path)
        if os.path.exists(full_path):
            core_modules["setup"] = full_path
            break

    # Find config files (settings.py or config.py)
    if isinstance(template_config, dict):
        for config_file in template_config.get("files", []):
            for base_path in template_config.get("paths", []):
                full_path = os.path.join(project_dir, base_path, config_file)
                if os.path.exists(full_path):
                    core_modules["config"] = full_path
                    break
            if core_modules["config"]:
                break

    return core_modules


def inject_project_metadata(
    target_dir: str,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
) -> None:
    """
    Inject project metadata into template files after template conversion.
    """
    try:
        core_modules = find_template_core_modules(target_dir)

        # Inject metadata to main.py
        if core_modules["main"]:
            with open(core_modules["main"], "r+") as f:
                content = f.read()
                content = content.replace("app_title", f'"{project_name}"')
                content = content.replace("app_description", f'"{description}"')
                f.seek(0)
                f.write(content)
                f.truncate()

        # Inject metadata to setup.py
        if core_modules["setup"]:
            with open(core_modules["setup"], "r+") as f:
                content = f.read()
                content = content.replace("<project_name>", project_name, 1)
                content = content.replace("<description>", description, 1)
                content = content.replace("<author>", author, 1)
                content = content.replace("<author_email>", author_email, 1)
                f.seek(0)
                f.write(content)
                f.truncate()

        # Inject metadata to config files
        if core_modules["config"]:
            with open(core_modules["config"], "r+") as f:
                content = f.read()
                content = content.replace("<project_name>", project_name)
                content = content.replace("<description>", description)
                f.seek(0)
                f.write(content)
                f.truncate()

    except Exception as e:
        print_error(f"Error during metadata injection: {e}")
        raise TemplateExceptions("Failed to inject metadata")


def create_venv(project_dir: str) -> str:
    """Create a virtual environment."""
    try:
        with console.status("[bold green]Setting up project environment..."):
            console.print("[yellow]Creating virtual environment...[/yellow]")
            venv_path = os.path.join(project_dir, ".venv")
            subprocess.run(["python", "-m", "venv", venv_path], check=True)

        if os.name == "nt":
            activate_venv = f"    {os.path.join(venv_path, 'Scripts', 'activate.bat')}"
        else:
            activate_venv = f"    source {os.path.join(venv_path, 'bin', 'activate')}"
            print_info(
                "venv created at "
                + venv_path
                + "\nTo activate the virtual environment, run:\n\n"
                + activate_venv,
            )
        return venv_path

    except Exception as e:
        print_error(f"Error during venv creation: {e}")
        raise BackendExceptions("Failed to create venv")


def install_dependencies(project_dir: str, venv_path: str) -> None:
    """Install project dependencies in the virtual environment."""
    try:
        if os.name == "nt":  # Windows
            pip_path = os.path.join(venv_path, "Scripts", "pip")
        else:  # Linux/Mac
            pip_path = os.path.join(venv_path, "bin", "pip")

        with console.status("[bold green]Installing dependencies..."):
            subprocess.run(
                [pip_path, "install", "-r", "requirements.txt"],
                cwd=project_dir,
                check=True,
            )

    except Exception as e:
        print_error(f"Error during dependency installation: {e}")
        raise BackendExceptions("Failed to install dependencies")


# TODO : modify this function
# def read_template_stack() -> Union[list, None]:
#     pass
