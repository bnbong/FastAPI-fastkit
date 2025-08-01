# --------------------------------------------------------------------------
# Poetry Package Manager Implementation
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import subprocess
from typing import List

from fastapi_fastkit import console
from fastapi_fastkit.core.exceptions import BackendExceptions
from fastapi_fastkit.utils.logging import debug_log, get_logger
from fastapi_fastkit.utils.main import handle_exception, print_error, print_success

from .base import BasePackageManager

logger = get_logger(__name__)


class PoetryManager(BasePackageManager):
    """Poetry package manager implementation."""

    def is_available(self) -> bool:
        """Check if Poetry is available on the system."""
        try:
            subprocess.run(
                ["poetry", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_dependency_file_name(self) -> str:
        """Get the dependency file name for Poetry."""
        return "pyproject.toml"

    def create_virtual_environment(self) -> str:
        """
        Create a virtual environment using Poetry.

        :return: Path to the virtual environment
        :raises: BackendExceptions if virtual environment creation fails
        """
        try:
            with console.status(
                "[bold green]Creating virtual environment with Poetry..."
            ):
                # Poetry automatically creates virtual environment when installing
                # First ensure we have a basic pyproject.toml
                pyproject_path = self.get_dependency_file_path()
                if not pyproject_path.exists():
                    # Create minimal pyproject.toml for Poetry
                    self._create_minimal_pyproject()

                # Get the virtual environment path from Poetry
                result = subprocess.run(
                    ["poetry", "env", "info", "--path"],
                    cwd=str(self.project_dir),
                    capture_output=True,
                    text=True,
                    check=False,  # Don't fail if venv doesn't exist yet
                )

                if result.returncode != 0:
                    # Create virtual environment with Poetry
                    subprocess.run(
                        ["poetry", "install", "--no-deps"],
                        cwd=str(self.project_dir),
                        check=True,
                        capture_output=True,
                        text=True,
                    )

                    # Get the path again
                    result = subprocess.run(
                        ["poetry", "env", "info", "--path"],
                        cwd=str(self.project_dir),
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                venv_path = result.stdout.strip()

            debug_log(f"Virtual environment created at {venv_path}", "info")
            print_success("Virtual environment created successfully with Poetry")
            return venv_path

        except subprocess.CalledProcessError as e:
            debug_log(f"Error creating virtual environment: {e.stderr}", "error")
            handle_exception(e, f"Error creating virtual environment: {str(e)}")
            raise BackendExceptions("Failed to create venv with Poetry")
        except OSError as e:
            debug_log(f"System error creating virtual environment: {e}", "error")
            handle_exception(e, f"Error creating virtual environment: {str(e)}")
            raise BackendExceptions(f"Failed to create venv with Poetry: {str(e)}")

    def _create_minimal_pyproject(self) -> None:
        """Create a minimal pyproject.toml for Poetry."""
        pyproject_content = """[tool.poetry]
name = "temp-project"
version = "0.1.0"
description = ""
authors = ["Author <author@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"

[tool.poetry.group.dev.dependencies]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""
        pyproject_path = self.get_dependency_file_path()
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(pyproject_content)

    def install_dependencies(self, venv_path: str) -> None:
        """
        Install dependencies using Poetry.

        :param venv_path: Path to the virtual environment
        :raises: BackendExceptions if dependency installation fails
        """
        try:
            pyproject_path = self.get_dependency_file_path()
            if not pyproject_path.exists():
                debug_log(f"pyproject.toml file not found at {pyproject_path}", "error")
                print_error(f"pyproject.toml file not found at {pyproject_path}")
                raise BackendExceptions("pyproject.toml file not found")

            # Install dependencies using Poetry
            with console.status("[bold green]Installing dependencies with Poetry..."):
                subprocess.run(
                    ["poetry", "install"],
                    cwd=str(self.project_dir),
                    check=True,
                    capture_output=True,
                    text=True,
                )

            debug_log("Dependencies installed successfully with Poetry", "info")
            print_success("Dependencies installed successfully with Poetry")

        except subprocess.CalledProcessError as e:
            debug_log(f"Error during dependency installation: {e.stderr}", "error")
            handle_exception(e, f"Error during dependency installation: {str(e)}")
            if hasattr(e, "stderr"):
                print_error(f"Error details: {e.stderr}")
            raise BackendExceptions("Failed to install dependencies with Poetry")
        except OSError as e:
            debug_log(f"System error during dependency installation: {e}", "error")
            handle_exception(e, f"Error during dependency installation: {str(e)}")
            raise BackendExceptions(
                f"Failed to install dependencies with Poetry: {str(e)}"
            )

    def generate_dependency_file(
        self,
        dependencies: List[str],
        project_name: str = "",
        author: str = "",
        author_email: str = "",
        description: str = "",
    ) -> None:
        """
        Generate a pyproject.toml file with the given dependencies and metadata.

        :param dependencies: List of dependency specifications
        :param project_name: Name of the project
        :param author: Author name
        :param author_email: Author email
        :param description: Project description
        """
        pyproject_path = self.get_dependency_file_path()

        try:
            # Create dependencies section for Poetry
            deps_section = ""
            for dep in dependencies:
                # Convert pip-style to poetry-style
                if "==" in dep:
                    name, version = dep.split("==", 1)
                    deps_section += f'{name} = "{version}"\n'
                else:
                    deps_section += f'{dep} = "*"\n'

            # Create basic pyproject.toml content for Poetry
            pyproject_content = f"""[tool.poetry]
name = "{project_name or 'fastapi-project'}"
version = "0.1.0"
description = "{description or 'A FastAPI project'}"
authors = ["{author or 'Author'} <{author_email or 'author@example.com'}>"]
readme = "README.md"
license = "MIT"
packages = [{{include = "src"}}]

[tool.poetry.dependencies]
python = "^3.8"
{deps_section}

[tool.poetry.group.dev.dependencies]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""

            with open(pyproject_path, "w", encoding="utf-8") as f:
                f.write(pyproject_content)

            debug_log(
                f"Generated {pyproject_path} with {len(dependencies)} dependencies",
                "info",
            )

        except (OSError, UnicodeEncodeError) as e:
            debug_log(f"Error generating pyproject.toml: {e}", "error")
            raise BackendExceptions(f"Failed to generate pyproject.toml: {str(e)}")

    def add_dependency(self, dependency: str, dev: bool = False) -> None:
        """
        Add a new dependency using Poetry.

        :param dependency: Dependency specification
        :param dev: Whether this is a development dependency
        """
        try:
            # Use Poetry's add command to add dependency
            cmd = ["poetry", "add"]
            if dev:
                cmd.append("--group=dev")
            cmd.append(dependency)

            subprocess.run(
                cmd,
                cwd=str(self.project_dir),
                check=True,
                capture_output=True,
                text=True,
            )

            debug_log(
                f"Added {'dev ' if dev else ''}dependency '{dependency}' with Poetry",
                "info",
            )

        except subprocess.CalledProcessError as e:
            debug_log(f"Error adding dependency with Poetry: {e}", "error")
            raise BackendExceptions(f"Failed to add dependency with Poetry: {str(e)}")
        except OSError as e:
            debug_log(f"System error adding dependency with Poetry: {e}", "error")
            raise BackendExceptions(f"Failed to add dependency with Poetry: {str(e)}")

    def initialize_project(
        self, project_name: str, author: str, author_email: str, description: str
    ) -> None:
        """
        Initialize a new Poetry project with metadata.

        :param project_name: Name of the project
        :param author: Author name
        :param author_email: Author email
        :param description: Project description
        """
        try:
            # Use Poetry init command with non-interactive mode
            subprocess.run(
                [
                    "poetry",
                    "init",
                    "--name",
                    project_name,
                    "--description",
                    description,
                    "--author",
                    f"{author} <{author_email}>",
                    "--license",
                    "MIT",
                    "--python",
                    "^3.8",
                    "--no-interaction",
                ],
                cwd=str(self.project_dir),
                check=True,
                capture_output=True,
                text=True,
            )

            debug_log(f"Initialized Poetry project: {project_name}", "info")

        except subprocess.CalledProcessError as e:
            debug_log(f"Error initializing Poetry project: {e}", "error")
            raise BackendExceptions(f"Failed to initialize Poetry project: {str(e)}")
        except OSError as e:
            debug_log(f"System error initializing Poetry project: {e}", "error")
            raise BackendExceptions(f"Failed to initialize Poetry project: {str(e)}")

    def lock_dependencies(self) -> None:
        """
        Generate Poetry lock file.

        :raises: BackendExceptions if lock generation fails
        """
        try:
            with console.status("[bold green]Generating Poetry lock file..."):
                subprocess.run(
                    ["poetry", "lock"],
                    cwd=str(self.project_dir),
                    check=True,
                    capture_output=True,
                    text=True,
                )

            debug_log("Poetry lock file generated successfully", "info")
            print_success("Poetry lock file generated successfully")

        except subprocess.CalledProcessError as e:
            debug_log(f"Error generating Poetry lock file: {e.stderr}", "error")
            handle_exception(e, f"Error generating Poetry lock file: {str(e)}")
            raise BackendExceptions("Failed to generate Poetry lock file")
        except OSError as e:
            debug_log(f"System error generating Poetry lock file: {e}", "error")
            handle_exception(e, f"Error generating Poetry lock file: {str(e)}")
            raise BackendExceptions(f"Failed to generate Poetry lock file: {str(e)}")

    def run_script(self, script_command: str) -> None:
        """
        Run a script using Poetry.

        :param script_command: Command to run
        :raises: BackendExceptions if script execution fails
        """
        try:
            subprocess.run(
                ["poetry", "run"] + script_command.split(),
                cwd=str(self.project_dir),
                check=True,
                capture_output=True,
                text=True,
            )

            debug_log(f"Poetry script executed successfully: {script_command}", "info")

        except subprocess.CalledProcessError as e:
            debug_log(f"Error running Poetry script: {e.stderr}", "error")
            raise BackendExceptions(f"Failed to run Poetry script: {str(e)}")
        except OSError as e:
            debug_log(f"System error running Poetry script: {e}", "error")
            raise BackendExceptions(f"Failed to run Poetry script: {str(e)}")

    def show_dependencies(self) -> str:
        """
        Show project dependencies using Poetry.

        :return: Dependencies information
        :raises: BackendExceptions if showing dependencies fails
        """
        try:
            result = subprocess.run(
                ["poetry", "show"],
                cwd=str(self.project_dir),
                check=True,
                capture_output=True,
                text=True,
            )

            return result.stdout

        except subprocess.CalledProcessError as e:
            debug_log(f"Error showing Poetry dependencies: {e.stderr}", "error")
            raise BackendExceptions(f"Failed to show Poetry dependencies: {str(e)}")
        except OSError as e:
            debug_log(f"System error showing Poetry dependencies: {e}", "error")
            raise BackendExceptions(f"Failed to show Poetry dependencies: {str(e)}")
