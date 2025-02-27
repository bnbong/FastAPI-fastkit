# --------------------------------------------------------------------------
# The Module defines backend operations for FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import subprocess
from typing import Dict, List

from fastapi_fastkit import console
from fastapi_fastkit.backend.transducer import copy_and_convert_template_file
from fastapi_fastkit.core.exceptions import BackendExceptions, TemplateExceptions
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.main import (
    handle_exception,
    print_error,
    print_info,
    print_success,
    print_warning,
)

# ------------------------------------------------------------
# Template Discovery Functions
# ------------------------------------------------------------


def find_template_core_modules(project_dir: str) -> Dict[str, str]:
    """
    Find core module files in the template project structure.
    Returns a dictionary with paths to main.py, setup.py, and config files.

    :param project_dir: Path to the project directory
    :return: Dictionary with paths to core modules
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

    # Find config files
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


def read_template_stack(template_path: str) -> List[str]:
    """
    Read the install_requires from setup.py-tpl in the template directory.
    Returns a list of required packages.

    :param template_path: Path to the template directory
    :return: List of required packages
    """
    setup_path = os.path.join(template_path, "setup.py-tpl")
    if not os.path.exists(setup_path):
        return []

    try:
        with open(setup_path, "r") as f:
            content = f.read()
            # Find the install_requires section using proper string matching
            if "install_requires: list[str] = [" in content:
                start_idx = content.find("install_requires: list[str] = [") + len(
                    "install_requires: list[str] = ["
                )
                end_idx = content.find("]", start_idx)
                if start_idx != -1 and end_idx != -1:
                    deps_str = content[start_idx:end_idx]
                    # Clean and parse the dependencies
                    deps = [
                        dep.strip().strip("'").strip('"')
                        for dep in deps_str.split(",")
                        if dep.strip() and not dep.isspace()
                    ]
                    return [dep for dep in deps if dep]  # Remove empty strings
    except Exception as e:
        handle_exception(e, "Error reading template dependencies")
        return []

    return []


# ------------------------------------------------------------
# Project Setup Functions
# ------------------------------------------------------------


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
        setup_py = core_modules.get("setup", "")
        config_py = core_modules.get("config", "")

        if setup_py and os.path.exists(setup_py):
            with open(setup_py, "r") as f:
                content = f.read()

            # Replace placeholders
            content = content.replace("<project_name>", project_name)
            content = content.replace("<author>", author)
            content = content.replace("<author_email>", author_email)
            content = content.replace("<description>", description)

            with open(setup_py, "w") as f:
                f.write(content)
            print_info("Injected metadata into setup.py")

        if config_py and os.path.exists(config_py):
            with open(config_py, "r") as f:
                content = f.read()

            content = content.replace("<project_name>", project_name)

            with open(config_py, "w") as f:
                f.write(content)
            print_info("Injected metadata into config file")

        # Try to find the readme file
        readme_files = ["README.md", "Readme.md", "readme.md"]
        for readme in readme_files:
            readme_path = os.path.join(target_dir, readme)
            if os.path.exists(readme_path):
                with open(readme_path, "r") as f:
                    content = f.read()

                content = content.replace(
                    "{FASTAPI TEMPLATE PROJECT NAME}", project_name
                )
                content = content.replace("{fill here}", author)

                with open(readme_path, "w") as f:
                    f.write(content)
                print_info("Injected metadata into README.md")
                break

    except Exception as e:
        handle_exception(e, "Failed to inject project metadata")
        raise BackendExceptions("Failed to inject project metadata")


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
    """
    Install project dependencies into the virtual environment.

    :param project_dir: Path to the project directory
    :param venv_path: Path to the virtual environment
    :return: None
    """
    try:
        if not os.path.exists(venv_path):
            print_error("Virtual environment does not exist. Creating it first.")
            venv_path = create_venv(project_dir)
            if not venv_path:
                raise BackendExceptions("Failed to create virtual environment")

        requirements_path = os.path.join(project_dir, "requirements.txt")
        if not os.path.exists(requirements_path):
            print_error(f"Requirements file not found at {requirements_path}")
            raise BackendExceptions("Requirements file not found")

        if os.name == "nt":  # Windows
            pip_path = os.path.join(venv_path, "Scripts", "pip")
        else:  # Unix-based
            pip_path = os.path.join(venv_path, "bin", "pip")

        # Upgrade pip
        subprocess.run(
            [pip_path, "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
            text=True,
        )

        with console.status("[bold green]Installing dependencies..."):
            subprocess.run(
                [pip_path, "install", "-r", "requirements.txt"],
                cwd=project_dir,
                check=True,
            )

        print_success("Dependencies installed successfully")

    except subprocess.CalledProcessError as e:
        handle_exception(e, f"Error during dependency installation: {str(e)}")
        if hasattr(e, "stderr"):
            print_error(f"Error details: {e.stderr}")
        raise BackendExceptions("Failed to install dependencies")
    except Exception as e:
        handle_exception(e, f"Error during dependency installation: {str(e)}")
        raise BackendExceptions(f"Failed to install dependencies: {str(e)}")


# ------------------------------------------------------------
# Add Route Functions
# ------------------------------------------------------------


def _ensure_project_structure(src_dir: str) -> Dict[str, str]:
    """
    Ensure the project structure exists for adding a new route.
    Creates necessary directories if they don't exist.

    :param src_dir: Source directory of the project
    :return: Dictionary with paths to target directories
    """
    if not os.path.exists(src_dir):
        raise BackendExceptions(f"Source directory not found at {src_dir}")

    # Define target directories
    target_dirs = {
        "api": os.path.join(src_dir, "api"),
        "api_routes": os.path.join(src_dir, "api", "routes"),
        "crud": os.path.join(src_dir, "crud"),
        "schemas": os.path.join(src_dir, "schemas"),
    }

    # Create directories and __init__.py files if needed
    for dir_name, dir_path in target_dirs.items():
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

            # Create __init__.py if it doesn't exist
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    pass

    return target_dirs


def _create_route_files(
    modules_dir: str, target_dirs: Dict[str, str], route_name: str
) -> None:
    """
    Create route files from templates.

    :param modules_dir: Path to the modules directory
    :param target_dirs: Dictionary with paths to target directories
    :param route_name: Name of the route to create
    """
    replacements = {"<new_route>": route_name}
    module_types = ["api/routes", "crud", "schemas"]

    for module_type in module_types:
        # Source template
        source = os.path.join(modules_dir, module_type, "new_route.py-tpl")

        # Target directory
        if module_type == "api/routes":
            target_dir = target_dirs["api_routes"]
        else:
            target_dir = target_dirs[module_type.split("/")[-1]]

        # Target file
        target = os.path.join(target_dir, f"{route_name}.py")

        if os.path.exists(target):
            print_warning(f"File {target} already exists, skipping...")
            continue

        if not copy_and_convert_template_file(source, target, replacements):
            print_warning(f"Failed to copy template file {source} to {target}")


def _handle_api_router_file(
    target_dirs: Dict[str, str], modules_dir: str, route_name: str
) -> None:
    """
    Handle the API router file - create or update.

    :param target_dirs: Dictionary with paths to target directories
    :param modules_dir: Path to the modules directory
    :param route_name: Name of the route to add
    """
    api_py_target = os.path.join(target_dirs["api"], "api.py")

    if os.path.exists(api_py_target):
        # Update existing api.py
        with open(api_py_target, "r") as f:
            api_content = f.read()

        # Check if router is already included
        router_import = f"from src.api.routes import {route_name}"
        if router_import not in api_content:
            with open(api_py_target, "a") as f:
                f.write(f"\n{router_import}\n")
                f.write(f"api_router.include_router({route_name}.router)\n")
            print_info(f"Added route {route_name} to existing api.py")
    else:
        # Create new api.py
        router_code = f"""
# --------------------------------------------------------------------------
# API router connector module
# --------------------------------------------------------------------------
from fastapi import APIRouter

from src.api.routes import {route_name}

api_router = APIRouter()
api_router.include_router({route_name}.router)

"""
        with open(api_py_target, "w") as tgt_file:
            tgt_file.write(router_code)


def _process_init_files(
    modules_dir: str, target_dirs: Dict[str, str], module_types: List[str]
) -> None:
    """
    Process __init__.py files if they don't exist.

    :param modules_dir: Path to the modules directory
    :param target_dirs: Dictionary with paths to target directories
    :param module_types: List of module types to process
    """
    for module_type in module_types:
        module_base = module_type.split("/")[0]
        init_source = os.path.join(modules_dir, module_base, "__init__.py-tpl")

        if os.path.exists(init_source):
            init_target_dir = target_dirs.get(module_base, None) or target_dirs.get(
                f"{module_base}_routes"
            )
            if init_target_dir:
                init_target = os.path.join(init_target_dir, "__init__.py")
                if not os.path.exists(init_target):
                    copy_and_convert_template_file(init_source, init_target)


def _update_main_app(src_dir: str, route_name: str) -> None:
    """
    Update the main application file to include the API router.
    Adds the router import and include statement at the end of the file.

    :param src_dir: Source directory of the project
    :param route_name: Name of the route to add
    """
    main_py_path = os.path.join(src_dir, "main.py")
    if not os.path.exists(main_py_path):
        print_warning("main.py not found. Please manually add the API router.")
        return

    with open(main_py_path, "r") as f:
        main_content = f.read()

    # Check if router is already imported or included
    router_import = "from src.api.api import api_router"
    router_include = "app.include_router(api_router"

    if router_import in main_content and router_include in main_content:
        # Router already fully configured, nothing to do
        return

    # Check if FastAPI app is defined
    if "app = FastAPI" not in main_content:
        print_warning(
            "FastAPI app instance not found in main.py. Please manually add router."
        )
        return

    # Add the router import if needed
    if router_import not in main_content:
        # Add import at the end of imports section or beginning of file
        lines = main_content.split("\n")

        # Find last import line
        last_import_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                last_import_idx = i

        if last_import_idx >= 0:
            # Insert after the last import
            lines.insert(last_import_idx + 1, router_import)
        else:
            # Insert at the beginning
            lines.insert(0, router_import)

        main_content = "\n".join(lines)

    # Add the router include
    if router_include not in main_content:
        if not main_content.endswith("\n"):
            main_content += "\n"

        main_content += f"\n# Include API router\napp.include_router(api_router)\n"

    # Write the updated content back to the file
    with open(main_py_path, "w") as f:
        f.write(main_content)

    print_info("Updated main.py to include the API router")


def add_new_route(project_dir: str, route_name: str) -> None:
    """
    Add a new API route to an existing FastAPI project.

    :param project_dir: Path to the project directory
    :param route_name: Name of the new route to add
    :return: None
    """
    try:
        # Setup paths
        modules_dir = os.path.join(settings.FASTKIT_TEMPLATE_ROOT, "modules")
        src_dir = os.path.join(project_dir, "src")

        # Ensure project structure exists
        target_dirs = _ensure_project_structure(src_dir)

        # Create route files
        _create_route_files(modules_dir, target_dirs, route_name)

        # Handle API router file
        _handle_api_router_file(target_dirs, modules_dir, route_name)

        # Process init files
        module_types = ["api/routes", "crud", "schemas"]
        _process_init_files(modules_dir, target_dirs, module_types)

        # Update main application
        _update_main_app(src_dir, route_name)

    except Exception as e:
        handle_exception(e, f"Error adding new route: {str(e)}")
        raise BackendExceptions(f"Failed to add new route: {str(e)}")
