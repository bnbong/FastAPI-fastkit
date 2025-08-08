# --------------------------------------------------------------------------
# The Module defines backend operations for FastAPI-fastkit CLI.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import re
from typing import Dict, List

from fastapi_fastkit import console
from fastapi_fastkit.backend.package_managers import PackageManagerFactory
from fastapi_fastkit.backend.transducer import copy_and_convert_template_file
from fastapi_fastkit.core.exceptions import BackendExceptions, TemplateExceptions
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.logging import debug_log, get_logger
from fastapi_fastkit.utils.main import (
    handle_exception,
    print_error,
    print_info,
    print_success,
    print_warning,
)

logger = get_logger(__name__)


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
    template_paths = settings.TEMPLATE_PATHS

    # Find main.py
    for main_path in template_paths["main"]:
        full_path = os.path.join(project_dir, main_path)
        if os.path.exists(full_path):
            core_modules["main"] = full_path
            break

    # Find setup.py
    for setup_path in template_paths["setup"]:
        full_path = os.path.join(project_dir, setup_path)
        if os.path.exists(full_path):
            core_modules["setup"] = full_path
            break

    # Find config file
    config_info = template_paths["config"]
    if isinstance(config_info, dict):
        for config_path in config_info["paths"]:
            for config_file in config_info["files"]:
                full_path = os.path.join(project_dir, config_path, config_file)
                if os.path.exists(full_path):
                    core_modules["config"] = full_path
                    break
            if core_modules["config"]:
                break

    return core_modules


def read_template_stack(template_path: str) -> List[str]:
    """
    Read dependencies from template requirements.txt-tpl file or setup.py-tpl file.

    :param template_path: Path to the template directory
    :return: List of dependencies
    """
    # First try requirements.txt-tpl
    req_file = os.path.join(template_path, "requirements.txt-tpl")
    if os.path.exists(req_file):
        try:
            with open(req_file, "r", encoding="utf-8") as f:
                deps = [dep.strip() for dep in f.readlines() if dep.strip()]
                return deps
        except (OSError, UnicodeDecodeError) as e:
            debug_log(
                f"Error reading template dependencies from {req_file}: {e}", "error"
            )
            return []

    # Fallback: try to read from setup.py-tpl for legacy templates
    setup_file = os.path.join(template_path, "setup.py-tpl")
    if os.path.exists(setup_file):
        try:
            with open(setup_file, "r", encoding="utf-8") as f:
                content = f.read()
                return _parse_setup_dependencies(content)
        except (OSError, UnicodeDecodeError) as e:
            debug_log(f"Error reading setup.py template: {e}", "error")

    return []


def _parse_setup_dependencies(content: str) -> List[str]:
    """
    Parse dependencies from setup.py content.

    :param content: setup.py file content
    :return: List of dependencies
    """
    # First try to find install_requires with list[str] type annotation (new format)
    list_match = re.search(
        r"install_requires:\s*list\[str\]\s*=\s*\[(.*?)\]",
        content,
        re.DOTALL,
    )
    if list_match:
        deps_str = list_match.group(1)
        # Split by lines and commas, clean up quotes
        deps = []
        for line in deps_str.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                # Remove quotes and trailing commas
                line = line.strip(" \",'")
                if line:
                    deps.append(line)
        return [dep for dep in deps if dep]  # Remove empty strings

    # Fallback to original install_requires parsing
    match = re.search(r"install_requires\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if match:
        deps_str = match.group(1).replace("\n", "").replace(" ", "")
        deps = [
            dep.strip().strip("'").strip('"')
            for dep in deps_str.split(",")
            if dep.strip() and not dep.isspace()
        ]
        return [dep for dep in deps if dep]  # Remove empty strings

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
        _process_setup_file(
            core_modules.get("setup", ""),
            project_name,
            author,
            author_email,
            description,
        )
        _process_config_file(core_modules.get("config", ""), project_name)

        print_success("Project metadata injected successfully")

    except Exception as e:
        debug_log(f"Failed to inject project metadata: {e}", "error")
        handle_exception(e, "Failed to inject project metadata")
        raise BackendExceptions("Failed to inject project metadata")


def _process_setup_file(
    setup_py: str, project_name: str, author: str, author_email: str, description: str
) -> None:
    """
    Process setup.py file and inject metadata.

    :param setup_py: Path to setup.py file
    :param project_name: Project name
    :param author: Author name
    :param author_email: Author email
    :param description: Project description
    """
    if not setup_py or not os.path.exists(setup_py):
        return

    try:
        with open(setup_py, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace placeholders
        replacements = {
            "<project_name>": project_name,
            "<author>": author,
            "<author_email>": author_email,
            "<description>": description,
        }

        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        with open(setup_py, "w", encoding="utf-8") as f:
            f.write(content)

        debug_log("Injected metadata into setup.py", "info")
        print_info("Injected metadata into setup.py")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error processing setup.py: {e}", "error")
        raise BackendExceptions(f"Failed to process setup.py: {e}")


def _process_config_file(config_py: str, project_name: str) -> None:
    """
    Process config file and inject project name.

    :param config_py: Path to config file
    :param project_name: Project name
    """
    if not config_py or not os.path.exists(config_py):
        return

    try:
        with open(config_py, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace project name placeholder
        content = content.replace("<project_name>", project_name)

        with open(config_py, "w", encoding="utf-8") as f:
            f.write(content)

        debug_log("Injected project name into config file", "info")
        print_info("Injected project name into config file")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error processing config file: {e}", "error")
        raise BackendExceptions(f"Failed to process config file: {e}")


def create_venv_with_manager(project_dir: str, manager_type: str = "pip") -> str:
    """
    Create a virtual environment using the specified package manager.

    :param project_dir: Path to the project directory
    :param manager_type: Type of package manager to use
    :return: Path to the virtual environment
    :raises: BackendExceptions if virtual environment creation fails
    """
    try:
        package_manager = PackageManagerFactory.create_manager(
            manager_type, project_dir, auto_detect=True
        )
        return package_manager.create_virtual_environment()
    except Exception as e:
        debug_log(
            f"Error creating virtual environment with {manager_type}: {e}", "error"
        )
        raise BackendExceptions(f"Failed to create virtual environment: {str(e)}")


def create_venv(project_dir: str) -> str:
    """
    Create a Python virtual environment in the project directory.

    This is a backward compatibility wrapper that uses pip by default.

    :param project_dir: Path to the project directory
    :return: Path to the virtual environment
    """
    return create_venv_with_manager(project_dir, "pip")


def install_dependencies_with_manager(
    project_dir: str, venv_path: str, manager_type: str = "pip"
) -> None:
    """
    Install dependencies using the specified package manager.

    :param project_dir: Path to the project directory
    :param venv_path: Path to the virtual environment
    :param manager_type: Type of package manager to use
    :return: None
    :raises: BackendExceptions if dependency installation fails
    """
    try:
        package_manager = PackageManagerFactory.create_manager(
            manager_type, project_dir, auto_detect=True
        )
        package_manager.install_dependencies(venv_path)
    except Exception as e:
        debug_log(f"Error installing dependencies with {manager_type}: {e}", "error")
        raise BackendExceptions(f"Failed to install dependencies: {str(e)}")


def install_dependencies(project_dir: str, venv_path: str) -> None:
    """
    Install dependencies in the virtual environment.

    This is a backward compatibility wrapper that uses pip by default.

    :param project_dir: Path to the project directory
    :param venv_path: Path to the virtual environment
    :return: None
    """
    install_dependencies_with_manager(project_dir, venv_path, "pip")


def generate_dependency_file_with_manager(
    project_dir: str,
    dependencies: List[str],
    manager_type: str = "pip",
    project_name: str = "",
    author: str = "",
    author_email: str = "",
    description: str = "",
) -> None:
    """
    Generate a dependency file using the specified package manager.

    :param project_dir: Path to the project directory
    :param dependencies: List of dependency specifications
    :param manager_type: Type of package manager to use
    :param project_name: Name of the project
    :param author: Author name
    :param author_email: Author email
    :param description: Project description
    :return: None
    :raises: BackendExceptions if dependency file generation fails
    """
    try:
        package_manager = PackageManagerFactory.create_manager(
            manager_type, project_dir, auto_detect=True
        )
        package_manager.generate_dependency_file(
            dependencies, project_name, author, author_email, description
        )
    except Exception as e:
        debug_log(f"Error generating dependency file with {manager_type}: {e}", "error")
        raise BackendExceptions(f"Failed to generate dependency file: {str(e)}")


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
    Handle API router file creation or update.

    :param target_dirs: Dictionary with paths to target directories
    :param modules_dir: Path to the modules directory
    :param route_name: Name of the route
    """
    api_dir = target_dirs["api"]
    api_router_file = os.path.join(api_dir, "api.py")

    if not os.path.exists(api_router_file):
        # Create api.py if it doesn't exist
        api_source = os.path.join(modules_dir, "api", "__init__.py-tpl")
        if os.path.exists(api_source):
            copy_and_convert_template_file(api_source, api_router_file)

    # Update API router to include new route
    if os.path.exists(api_router_file):
        _update_api_router(api_router_file, route_name)


def _update_api_router(api_router_file: str, route_name: str) -> None:
    """
    Update API router file to include new route.

    :param api_router_file: Path to API router file
    :param route_name: Name of the route
    """
    try:
        with open(api_router_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if route is already included
        route_import = f"from .routes import {route_name}"
        route_include = f"api_router.include_router({route_name}.router"

        if route_import in content and route_include in content:
            return  # Already included

        # Add import if not present
        if route_import not in content:
            # Find where to add the import
            lines = content.split("\n")
            last_import_idx = -1
            for i, line in enumerate(lines):
                if line.startswith("from .routes import") or line.startswith(
                    "from routes import"
                ):
                    last_import_idx = i

            if last_import_idx >= 0:
                lines.insert(last_import_idx + 1, route_import)
            else:
                # Add at the end of imports section
                for i, line in enumerate(lines):
                    if (
                        not line.startswith("from")
                        and not line.startswith("import")
                        and line.strip()
                    ):
                        lines.insert(i, route_import)
                        break

            content = "\n".join(lines)

        # Add router inclusion if not present
        if route_include not in content:
            # Add before the last line or at the end
            if content.strip():
                content += f'\napi_router.include_router({route_name}.router, prefix="/{route_name}", tags=["{route_name}"])\n'
            else:
                content = f'api_router.include_router({route_name}.router, prefix="/{route_name}", tags=["{route_name}"])\n'

        with open(api_router_file, "w", encoding="utf-8") as f:
            f.write(content)

        debug_log(f"Updated API router to include {route_name}", "info")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error updating API router: {e}", "error")


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

    try:
        with open(main_py_path, "r", encoding="utf-8") as f:
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

        # Add router inclusion if needed
        if router_include not in main_content:
            # Add at the end of the file
            main_content += "\napp.include_router(api_router)\n"

        with open(main_py_path, "w", encoding="utf-8") as f:
            f.write(main_content)

        debug_log(f"Updated main.py to include router for {route_name}", "info")

    except (OSError, UnicodeDecodeError) as e:
        debug_log(f"Error updating main.py: {e}", "error")
        print_warning(f"Failed to update main.py: {e}")


def add_new_route(project_dir: str, route_name: str) -> None:
    """
    Add a new API route to an existing FastAPI project.

    :param project_dir: Path to the project directory
    :param route_name: Name of the new route to add
    :raises BackendExceptions: If route addition fails
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

        debug_log(f"Successfully added new route: {route_name}", "info")
        print_success(f"Route '{route_name}' has been added successfully!")

    except (OSError, PermissionError) as e:
        debug_log(f"File system error while adding route {route_name}: {e}", "error")
        handle_exception(e, f"Error adding new route: {str(e)}")
        raise BackendExceptions(f"Failed to add new route: {str(e)}")
    except BackendExceptions:
        # Re-raise our own exceptions
        raise
    except Exception as e:
        debug_log(f"Unexpected error while adding route {route_name}: {e}", "error")
        handle_exception(e, f"Error adding new route: {str(e)}")
        raise BackendExceptions(f"Failed to add new route: {str(e)}")
