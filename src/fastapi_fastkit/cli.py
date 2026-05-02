# --------------------------------------------------------------------------
# The Module defines main and core CLI operations for FastAPI-fastkit.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import atexit
import os
import shutil
import subprocess
import sys
from typing import Union, cast

import click
from click import Command, Context
from rich import print
from rich.panel import Panel

from fastapi_fastkit.backend.interactive import InteractiveConfigBuilder
from fastapi_fastkit.backend.interactive.selectors import display_feature_catalog
from fastapi_fastkit.backend.main import (
    add_new_route,
    ask_create_project_folder,
    create_venv_with_manager,
    deploy_template_with_folder_option,
    find_template_core_modules,
    generate_dependency_file_with_manager,
    get_deployment_success_message,
    inject_project_metadata,
    install_dependencies_with_manager,
    read_template_stack,
)
from fastapi_fastkit.core.exceptions import CLIExceptions
from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.utils.logging import get_logger, setup_logging
from fastapi_fastkit.utils.main import console as utils_console
from fastapi_fastkit.utils.main import (
    create_info_table,
    is_fastkit_project,
    print_error,
    print_info,
    print_success,
    print_warning,
    validate_email,
)

from . import __version__

console = utils_console


def _cleanup_failed_project(
    project_dir: str, user_workspace: str, create_project_folder: bool
) -> None:
    """
    Clean up a partially created project after an error.

    Only deletes a freshly created project folder. When the project was deployed
    in-place (create_project_folder=False), project_dir equals the user's workspace,
    and removing it would destroy unrelated files, so no cleanup is performed.
    """
    if not create_project_folder:
        return
    if not project_dir or not os.path.exists(project_dir):
        return
    if os.path.abspath(project_dir) == os.path.abspath(user_workspace):
        return
    shutil.rmtree(project_dir, ignore_errors=True)


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.version_option(__version__, prog_name="fastapi-fastkit")
@click.pass_context
def fastkit_cli(ctx: Context, debug: bool) -> Union["Command", None]:
    """
    main FastAPI-fastkit CLI operation group
    """
    settings = FastkitConfig()
    ctx.ensure_object(dict)

    if debug:
        print_warning("running at debugging mode!!")
        settings.set_debug_mode()

    ctx.obj["settings"] = settings

    # Setup logging and get debug capture if debug mode is enabled
    debug_capture = setup_logging(settings=settings)
    ctx.obj["debug_capture"] = debug_capture

    # If debug mode is enabled, start capturing output
    if debug_capture:
        debug_capture.__enter__()
        # Log CLI invocation
        logger = get_logger()
        logger.info(f"CLI invoked with debug mode: {' '.join(sys.argv)}")

        # Register cleanup function for when the CLI exits
        def cleanup_debug_capture() -> None:
            try:
                debug_capture.__exit__(None, None, None)
                logger.info("FastAPI-fastkit CLI session ended")
            except Exception:
                pass  # Fail silently during cleanup

        atexit.register(cleanup_debug_capture)

    return None


@fastkit_cli.command()
@click.pass_context
def echo(ctx: Context) -> None:
    """
    About FastAPI-fastkit
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
@click.pass_context
def list_templates(ctx: Context) -> None:
    """
    Display the list of available templates.
    """
    settings = ctx.obj["settings"]
    template_dir = settings.FASTKIT_TEMPLATE_ROOT

    if not os.path.exists(template_dir):
        print_error("Template directory not found.")
        return

    excluded_dirs = ["__pycache__", "modules"]
    templates = [
        d
        for d in os.listdir(template_dir)
        if os.path.isdir(os.path.join(template_dir, d)) and d not in excluded_dirs
    ]

    if not templates:
        print_warning("No available templates.")
        return

    template_data = {}
    for template in templates:
        template_path = os.path.join(template_dir, template)
        readme_path = os.path.join(template_path, "README.md-tpl")

        description = "No description"
        if os.path.exists(readme_path):
            with open(readme_path, "r") as f:
                first_line = f.readline().strip()
                if first_line.startswith("# "):
                    description = first_line[2:]

        template_data[template] = description

    table = create_info_table("Available Templates", template_data)
    console.print(table)


@fastkit_cli.command()
@click.pass_context
def list_features(ctx: Context) -> None:
    """
    Display the list of available features and packages in the catalog.

    Shows all available features that can be selected during interactive
    project creation, along with their associated packages.
    """
    settings = ctx.obj["settings"]

    display_feature_catalog(settings.PACKAGE_CATALOG, settings.FEATURE_DESCRIPTIONS)


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
@click.option(
    "--package-manager",
    help="Package manager to use for the project.",
    type=click.Choice(["pip", "uv", "pdm", "poetry"]),
    default=None,
)
@click.pass_context
def startdemo(
    ctx: Context,
    template: str,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
    package_manager: str,
) -> None:
    """
    Create a new FastAPI project from templates and inject metadata.
    """
    # TODO : add --template-name option to specify the template name
    settings = ctx.obj["settings"]

    template_dir = settings.FASTKIT_TEMPLATE_ROOT
    click.echo(f"Deploying FastAPI project using '{template}' template")
    target_template = os.path.join(template_dir, template)

    if settings.DEBUG_MODE:
        logger = get_logger()
        logger.info(f"Template path: {target_template}")

    click.echo(f"Template path: {target_template}")

    if not os.path.exists(target_template):
        print_error(f"Template '{template}' does not exist in '{template_dir}'.")
        raise CLIExceptions(
            f"Template '{template}' does not exist in '{template_dir}'."
        )
    table = create_info_table(
        "Project Information",
        {
            "Project Name": project_name,
            "Author": author,
            "Author Email": author_email,
            "Description": description,
        },
    )

    console.print("\n")
    console.print(table)

    template_deps = read_template_stack(target_template)
    if template_deps:
        deps_table = create_info_table(
            "Template Dependencies",
            {f"Dependency {i + 1}": dep for i, dep in enumerate(template_deps)},
        )
        console.print("\n")
        console.print(deps_table)

    # Package manager selection
    if not package_manager:
        console.print("\n[bold]Available Package Managers:[/bold]")
        package_manager_table = create_info_table(
            "Package Managers",
            {
                f"{manager.upper()}": config["description"]
                for manager, config in settings.PACKAGE_MANAGER_CONFIG.items()
            },
        )
        console.print(package_manager_table)
        console.print("\n")

        package_manager = click.prompt(
            "Select package manager",
            type=click.Choice(settings.SUPPORTED_PACKAGE_MANAGERS),
            default=settings.DEFAULT_PACKAGE_MANAGER,
            show_choices=True,
            show_default=True,
        )

    confirm = click.confirm(
        "\nDo you want to proceed with project creation?", default=False
    )
    if not confirm:
        print_error("Project creation aborted!")
        return

    # Ask user whether to create a new project folder
    create_project_folder = ask_create_project_folder(project_name)

    try:
        user_local = settings.USER_WORKSPACE

        project_dir, _ = deploy_template_with_folder_option(
            target_template, user_local, project_name, create_project_folder
        )

        inject_project_metadata(
            project_dir, project_name, author, author_email, description
        )

        venv_path = create_venv_with_manager(project_dir, package_manager)
        install_dependencies_with_manager(project_dir, venv_path, package_manager)

        success_message = get_deployment_success_message(
            template, project_name, user_local, create_project_folder
        )
        print_success(success_message)

    except Exception as e:
        if settings.DEBUG_MODE:
            logger = get_logger()
            logger.exception(f"Error during project creation in startdemo: {str(e)}")
        print_error(f"Error during project creation: {str(e)}")


@fastkit_cli.command(context_settings={"ignore_unknown_options": True})
@click.option(
    "--interactive",
    is_flag=True,
    default=False,
    help=(
        "Enable interactive mode for guided project setup. Walks through an "
        "architecture preset (minimal / single-module / classic-layered / "
        "domain-starter, default: domain-starter), then feature selection."
    ),
)
@click.option(
    "--project-name",
    default=None,
    help="The name of the new FastAPI project.",
)
@click.option("--author", default=None, help="The name of the project author.")
@click.option(
    "--author-email",
    default=None,
    help="The email of the project author.",
    type=str,
)
@click.option(
    "--description",
    default=None,
    help="The description of the new FastAPI project.",
)
@click.option(
    "--package-manager",
    help="Package manager to use for the project.",
    type=click.Choice(["pip", "uv", "pdm", "poetry"]),
    default=None,
)
@click.pass_context
def init(
    ctx: Context,
    interactive: bool,
    project_name: str,
    author: str,
    author_email: str,
    description: str,
    package_manager: str,
) -> None:
    """
    Start a FastAPI project setup.

    Use --interactive for guided setup. Interactive mode prompts for an
    architecture preset (``minimal`` / ``single-module`` / ``classic-layered``
    / ``domain-starter`` — default: ``domain-starter``) and then walks
    through feature selection (database, auth, testing, deployment, ...).

    Without --interactive, creates an empty project with predefined stacks.

    This command will automatically create a new FastAPI project directory
    and a python virtual environment. Dependencies will be automatically
    installed based on the selected features or stack.
    """
    settings = ctx.obj["settings"]

    # Interactive mode - use InteractiveConfigBuilder
    if interactive:
        print_info("Starting interactive project setup...")

        builder = InteractiveConfigBuilder(settings)
        config = builder.run_interactive_flow()

        # User cancelled
        if not config:
            return

        # Extract configuration
        project_name = cast(str, config.get("project_name", ""))
        author = cast(str, config.get("author", ""))
        author_email = cast(str, config.get("author_email", ""))
        description = cast(str, config.get("description", ""))
        package_manager = config.get(
            "package_manager", settings.DEFAULT_PACKAGE_MANAGER
        )
        all_dependencies = config.get("all_dependencies", [])

        # Check if project already exists
        project_dir = os.path.join(settings.USER_WORKSPACE, project_name)
        if os.path.exists(project_dir):
            print_error(f"Error: Project '{project_name}' already exists.")
            return

        # Ask user whether to create a new project folder
        create_project_folder = ask_create_project_folder(project_name)

        try:
            user_local = settings.USER_WORKSPACE

            # Pick the base template from the architecture preset chosen
            # earlier in the interactive flow. Older callers without a
            # preset fall back to ``minimal`` (= fastapi-empty), preserving
            # pre-#45 behaviour.
            from fastapi_fastkit.backend.project_builder import (
                PresetLayoutStrategist,
            )

            preset_id = config.get("architecture_preset")
            strategist = PresetLayoutStrategist(preset_id)
            template = strategist.base_template
            template_dir = settings.FASTKIT_TEMPLATE_ROOT
            target_template = os.path.join(template_dir, template)

            if not os.path.exists(target_template):
                print_error(
                    f"Template '{template}' does not exist in '{template_dir}'."
                )
                raise CLIExceptions(
                    f"Template '{template}' does not exist in '{template_dir}'."
                )

            # Deploy template
            project_dir, _ = deploy_template_with_folder_option(
                target_template, user_local, project_name, create_project_folder
            )

            # Inject project metadata
            inject_project_metadata(
                project_dir, project_name, author, author_email, description
            )

            # Generate dependency file with collected dependencies
            generate_dependency_file_with_manager(
                project_dir,
                all_dependencies,
                package_manager,
                project_name,
                author,
                author_email,
                description,
            )

            # Update setup.py install_requires with selected dependencies
            from fastapi_fastkit.backend.main import update_setup_py_dependencies

            update_setup_py_dependencies(project_dir, all_dependencies)

            print_success(
                f"Generated dependency file with {len(all_dependencies)} packages"
            )

            # Generate stack-specific code and configurations
            from fastapi_fastkit.backend.project_builder.config_generator import (
                DynamicConfigGenerator,
            )

            generator = DynamicConfigGenerator(config, project_dir)

            # main.py overlay — only regenerated for presets that ship a
            # placeholder app (minimal, single-module). For richer presets
            # (classic-layered, domain-starter) we keep the template's
            # router-aware main.py intact.
            #
            # The strategist's ``main_py_target`` is always ``src/main.py``
            # for both regenerate-main presets, and both fastapi-empty and
            # fastapi-single-module ship that file, so we can write
            # straight to the strategist's path without a flat-``main.py``
            # fallback branch.
            if strategist.should_regenerate_main:
                main_py_path = strategist.main_py_target(project_dir)
                main_py_path.parent.mkdir(parents=True, exist_ok=True)
                main_py_path.write_text(generator.generate_main_py())
            else:
                print_info(
                    f"Preserving template-shipped main.py for preset "
                    f"'{strategist.preset_id}'."
                )

            # Generate database configuration if selected — preset chooses
            # where the file lives so it sits next to the existing structure.
            db_info = config.get("database", {})
            if isinstance(db_info, dict) and db_info.get("type") != "None":
                db_config_content = generator.generate_database_config()
                if db_config_content:
                    db_config_path = strategist.db_config_target(project_dir)
                    db_config_path.parent.mkdir(parents=True, exist_ok=True)
                    db_config_path.write_text(db_config_content)

            # Generate auth configuration if selected
            auth_type = config.get("authentication", "None")
            if auth_type != "None":
                auth_config_content = generator.generate_auth_config()
                if auth_config_content:
                    auth_config_path = strategist.auth_config_target(project_dir)
                    auth_config_path.parent.mkdir(parents=True, exist_ok=True)
                    auth_config_path.write_text(auth_config_content)

            # Generate test configuration if testing selected
            testing_type = config.get("testing", "None")
            if testing_type != "None":
                test_config_content = generator.generate_test_config()
                if test_config_content:
                    test_config_path = os.path.join(project_dir, "pytest.ini")
                    with open(test_config_path, "w") as f:
                        f.write(test_config_content)

            # Generate Docker files if deployment selected
            deployment = config.get("deployment", [])
            if deployment and deployment != ["None"]:
                # Thread the preset-aware app module so the generated
                # Dockerfile's ``CMD ["uvicorn", "<module>:app", ...]``
                # matches the layout the user actually generated. Default
                # ``src.main:app`` only works for minimal / single-module /
                # classic-layered; domain-starter needs ``src.app.main:app``.
                generator.generate_docker_files(app_module=strategist.app_module)
                print_success("Generated Docker deployment files")

            # Surface preset-specific warnings (e.g. "you picked a preset
            # whose shipped main.py we kept; CORS/Prometheus must be wired
            # manually").
            for warning in strategist.compatibility_warnings(config):
                print_warning(warning, title="Preset compatibility")

            print_success("Generated configuration files for selected stack")

            # Create virtual environment and install dependencies
            venv_path = create_venv_with_manager(project_dir, package_manager)
            install_dependencies_with_manager(project_dir, venv_path, package_manager)

            success_message = get_deployment_success_message(
                template, project_name, user_local, create_project_folder
            )
            print_success(success_message)

            print_info(
                "To start your project, run 'fastkit runserver' at newly created FastAPI project directory"
            )

        except Exception as e:
            if settings.DEBUG_MODE:
                logger = get_logger()
                logger.exception(f"Error during project creation in init: {str(e)}")
            print_error(f"Error during project creation: {str(e)}")
            _cleanup_failed_project(
                project_dir, settings.USER_WORKSPACE, create_project_folder
            )

        return

    # Non-interactive mode (original behavior)
    # Require parameters if not interactive
    if not project_name:
        project_name = click.prompt("Enter the project name", type=str)
    if not author:
        author = click.prompt("Enter the author name", type=str)
    if not author_email:
        while True:
            author_email = click.prompt("Enter the author email", type=str)
            # Simple validation
            if "@" in author_email and "." in author_email:
                break
            print_error("Invalid email format. Please try again.")
    if not description:
        description = click.prompt("Enter the project description", type=str)

    project_dir = os.path.join(settings.USER_WORKSPACE, project_name)

    if os.path.exists(project_dir):
        print_error(f"Error: Project '{project_name}' already exists.")
        return

    # Display project information
    project_info_table = create_info_table(
        "Project Information",
        {
            "Project Name": project_name,
            "Author": author,
            "Author Email": author_email,
            "Description": description,
        },
    )
    console.print("\n")
    console.print(project_info_table)

    # Display available stacks
    console.print("\n[bold]Available Stacks and Dependencies:[/bold]")

    for stack_name, deps in settings.PROJECT_STACKS.items():
        table = create_info_table(
            f"{stack_name.upper()} Stack",
            {f"Dependency {i + 1}": dep for i, dep in enumerate(deps)},
        )
        console.print(table)
        console.print("\n")

    stack = click.prompt(
        "Select stack",
        type=click.Choice(list(settings.PROJECT_STACKS.keys())),
        show_choices=True,
    )

    # Package manager selection
    if not package_manager:
        console.print("\n[bold]Available Package Managers:[/bold]")
        package_manager_table = create_info_table(
            "Package Managers",
            {
                f"{manager.upper()}": config["description"]
                for manager, config in settings.PACKAGE_MANAGER_CONFIG.items()
            },
        )
        console.print(package_manager_table)
        console.print("\n")

        package_manager = click.prompt(
            "Select package manager",
            type=click.Choice(settings.SUPPORTED_PACKAGE_MANAGERS),
            default=settings.DEFAULT_PACKAGE_MANAGER,
            show_choices=True,
            show_default=True,
        )

    template = "fastapi-empty"
    template_dir = settings.FASTKIT_TEMPLATE_ROOT
    target_template = os.path.join(template_dir, template)

    if not os.path.exists(target_template):
        print_error(f"Template '{template}' does not exist in '{template_dir}'.")
        raise CLIExceptions(
            f"Template '{template}' does not exist in '{template_dir}'."
        )

    confirm = click.confirm(
        "\nDo you want to proceed with project creation?", default=False
    )
    if not confirm:
        print_error("Project creation aborted!")
        return

    # Ask user whether to create a new project folder
    create_project_folder = ask_create_project_folder(project_name)

    try:
        user_local = settings.USER_WORKSPACE

        project_dir, _ = deploy_template_with_folder_option(
            target_template, user_local, project_name, create_project_folder
        )

        inject_project_metadata(
            project_dir, project_name, author, author_email, description
        )

        deps_table = create_info_table(
            f"Creating Project: {project_name}", {"Component": "Collected"}
        )

        # Generate dependency file using selected package manager
        dependencies = settings.PROJECT_STACKS[stack]
        generate_dependency_file_with_manager(
            project_dir,
            dependencies,
            package_manager,
            project_name,
            author,
            author_email,
            description,
        )

        for dep in dependencies:
            deps_table.add_row(dep, "✓")

        console.print(deps_table)

        # Create virtual environment and install dependencies with selected package manager
        venv_path = create_venv_with_manager(project_dir, package_manager)
        install_dependencies_with_manager(project_dir, venv_path, package_manager)

        success_message = get_deployment_success_message(
            template, project_name, user_local, create_project_folder
        )
        print_success(success_message)

        print_info(
            "To start your project, run 'fastkit runserver' at newly created FastAPI project directory"
        )

    except Exception as e:
        if settings.DEBUG_MODE:
            logger = get_logger()
            logger.exception(f"Error during project creation in init: {str(e)}")
        print_error(f"Error during project creation: {str(e)}")
        _cleanup_failed_project(
            project_dir, settings.USER_WORKSPACE, create_project_folder
        )


@fastkit_cli.command()
@click.argument("route_name")
@click.argument("project_dir", default=".")
@click.pass_context
def addroute(ctx: Context, route_name: str, project_dir: str) -> None:
    """
    Add a new route to the FastAPI project.

    Examples:\n
        fastkit addroute user .          # Add 'user' route to current directory
        fastkit addroute user my_project # Add 'user' route to 'my_project' in workspace
    """
    settings = ctx.obj["settings"]

    if project_dir == ".":
        actual_project_dir = os.getcwd()
        project_name = os.path.basename(actual_project_dir)
    else:
        user_local = settings.USER_WORKSPACE
        actual_project_dir = os.path.join(user_local, project_dir)
        project_name = project_dir

    # Check if project exists
    if not os.path.exists(actual_project_dir):
        if project_dir == ".":
            print_error("Current directory is not a valid project directory.")
        else:
            print_error(
                f"Project '{project_dir}' does not exist in '{settings.USER_WORKSPACE}'."
            )
        return

    # Verify it's a fastkit project
    if not is_fastkit_project(actual_project_dir):
        if project_dir == ".":
            print_error("Current directory is not a FastAPI-fastkit project.")
        else:
            print_error(f"'{project_dir}' is not a FastAPI-fastkit project.")
        return

    # Validate route name
    if not route_name.isidentifier():
        print_error(f"Route name '{route_name}' is not a valid Python identifier.")
        return

    # Route name shouldn't match reserved keywords
    import keyword

    if keyword.iskeyword(route_name):
        print_error(
            f"Route name '{route_name}' is a Python keyword and cannot be used."
        )
        return

    try:
        # Show information about the operation
        table = create_info_table(
            "Adding New Route",
            {
                "Project": project_name,
                "Route Name": route_name,
                "Target Directory": actual_project_dir,
            },
        )
        console.print(table)

        if project_dir == ".":
            confirm_message = (
                f"\nDo you want to add route '{route_name}' to the current project?"
            )
        else:
            confirm_message = f"\nDo you want to add route '{route_name}' to project '{project_name}'?"

        confirm = click.confirm(confirm_message, default=True)
        if not confirm:
            print_error("Operation cancelled!")
            return

        # Add the new route
        add_new_route(actual_project_dir, route_name)

        if project_dir == ".":
            print_success(
                f"Successfully added new route '{route_name}' to the current project!"
            )
        else:
            print_success(
                f"Successfully added new route '{route_name}' to project '{project_name}'!"
            )

    except Exception as e:
        logger = get_logger()
        logger.exception(f"Error during route addition: {str(e)}")
        print_error(f"Error during route addition: {str(e)}")


@fastkit_cli.command()
@click.argument("project_name")
@click.pass_context
def deleteproject(ctx: Context, project_name: str) -> None:
    """
    Delete a FastAPI project.
    """
    settings = ctx.obj["settings"]
    user_local = settings.USER_WORKSPACE
    project_dir = os.path.join(user_local, project_name)

    if not os.path.exists(project_dir):
        print_error(f"Project '{project_name}' does not exist in '{user_local}'.")
        return

    if not is_fastkit_project(project_dir):
        print_error(f"'{project_name}' is not a FastAPI-fastkit project.")
        return

    confirm = click.confirm(
        f"\nDo you want to delete project '{project_name}' at '{project_dir}'?",
        default=False,
    )
    if not confirm:
        print_error("Project deletion cancelled!")
        return

    try:
        shutil.rmtree(project_dir)
        print_success(f"Project '{project_name}' has been deleted successfully!")

    except Exception as e:
        logger = get_logger()
        logger.exception(f"Error during project deletion: {e}")
        print_error(f"Error during project deletion: {e}")


def _derive_app_module(project_dir: str, main_path: str) -> str:
    """Convert a discovered ``main.py`` path into a uvicorn ``module:attr``.

    Templates can place ``main.py`` anywhere under the project (``main.py``,
    ``src/main.py``, ``src/app/main.py``, ...). The previous ``"src/"`` /
    ``""`` heuristic mis-mapped the domain-starter layout (``src/app/main.py``
    → wrongly produced ``src.main:app``); deriving the dotted path from the
    actual relative location avoids that drift for any future layout too.
    """
    rel_path = os.path.relpath(main_path, project_dir)
    module_part = os.path.splitext(rel_path)[0].replace(os.sep, ".")
    return f"{module_part}:app"


@fastkit_cli.command()
@click.option(
    "--host",
    default="127.0.0.1",
    show_default=True,
    help="Host to bind the server",
)
@click.option(
    "--port",
    default=8000,
    show_default=True,
    help="Port to bind the server",
)
@click.option(
    "--reload/--no-reload",
    default=True,
    show_default=True,
    help="Enable/disable auto-reload on code changes",
)
@click.option(
    "--workers",
    default=1,
    show_default=True,
    help="Number of worker processes",
)
@click.pass_context
def runserver(
    ctx: Context,
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True,
    workers: int = 1,
) -> None:
    """
    Run the FastAPI server for the current project.
    """
    settings = ctx.obj["settings"]
    project_dir = settings.USER_WORKSPACE

    # Check for virtual environment
    venv_path = os.path.join(project_dir, ".venv")
    if not os.path.exists(venv_path) or not os.path.isdir(venv_path):
        print_error(
            "Virtual environment not found. Is this a project deployed with Fastkit?"
        )
        confirm = click.confirm(
            "Do you want to continue with system Python?", default=False
        )
        if not confirm:
            return
        venv_python = None
    else:
        if os.name == "nt":  # Windows
            venv_python = os.path.join(venv_path, "Scripts", "python.exe")
        else:  # Unix/Linux/Mac
            venv_python = os.path.join(venv_path, "bin", "python")

        if not os.path.exists(venv_python):
            print_error(
                f"Python interpreter not found in virtual environment: {venv_python}"
            )
            confirm = click.confirm(
                "Do you want to continue with system Python?", default=False
            )
            if not confirm:
                return
            venv_python = None

    core_modules = find_template_core_modules(project_dir)
    if not core_modules["main"]:
        print_error(f"Could not find 'main.py' in '{project_dir}'.")
        return

    main_path = core_modules["main"]
    app_module = _derive_app_module(project_dir, main_path)

    if venv_python:
        print_info(f"Using Python from virtual environment: {venv_python}")
        command = [
            venv_python,
            "-m",
            "uvicorn",
            app_module,
            "--host",
            host,
            "--port",
            str(port),
            "--workers",
            str(workers),
        ]
    else:
        command = [
            "uvicorn",
            app_module,
            "--host",
            host,
            "--port",
            str(port),
            "--workers",
            str(workers),
        ]

    if reload:
        command.append("--reload")

    try:
        print_success(f"Starting FastAPI server at {host}:{port}...")

        # Set up environment variables for the subprocess
        env = os.environ.copy()
        if venv_python:
            python_path = os.path.dirname(os.path.dirname(venv_python))
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = f"{python_path}:{env['PYTHONPATH']}"
            else:
                env["PYTHONPATH"] = python_path

        # Run the server with the configured environment
        subprocess.run(command, check=True, env=env)
    except subprocess.CalledProcessError as e:
        logger = get_logger()
        logger.exception(f"Failed to start FastAPI server: {e}")
        print_error(f"Failed to start FastAPI server.\n{e}")
    except FileNotFoundError as e:
        logger = get_logger()
        logger.exception(f"FileNotFoundError when starting server: {e}")
        if venv_python:
            print_error(
                "Failed to run Python from the virtual environment. Make sure uvicorn is installed in the project's virtual environment."
            )
        else:
            print_error(
                "uvicorn not found. Make sure it's installed in your system Python."
            )
