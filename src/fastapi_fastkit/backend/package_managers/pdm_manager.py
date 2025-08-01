# --------------------------------------------------------------------------
# PDM Package Manager Implementation
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import subprocess
import sys
from typing import List

from fastapi_fastkit import console
from fastapi_fastkit.core.exceptions import BackendExceptions
from fastapi_fastkit.utils.logging import debug_log, get_logger
from fastapi_fastkit.utils.main import handle_exception, print_error, print_success

from .base import BasePackageManager

logger = get_logger(__name__)


class PdmManager(BasePackageManager):
    """PDM package manager implementation."""

    def is_available(self) -> bool:
        """Check if PDM is available on the system."""
        try:
            subprocess.run(
                ["pdm", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_dependency_file_name(self) -> str:
        """Get the dependency file name for PDM."""
        return "pyproject.toml"

    def create_virtual_environment(self) -> str:
        """
        Create a virtual environment using PDM.

        :return: Path to the virtual environment
        :raises: BackendExceptions if virtual environment creation fails
        """
        venv_path = str(self.project_dir / ".venv")

        try:
            with console.status("[bold green]Creating virtual environment with PDM..."):
                # PDM can create virtual environment in specific location
                subprocess.run(
                    ["pdm", "venv", "create", "--name", ".venv", sys.executable],
                    cwd=str(self.project_dir),
                    check=True,
                    capture_output=True,
                    text=True,
                )

            debug_log(f"Virtual environment created at {venv_path}", "info")
            print_success("Virtual environment created successfully with PDM")
            return venv_path

        except subprocess.CalledProcessError as e:
            debug_log(f"Error creating virtual environment: {e.stderr}", "error")
            handle_exception(e, f"Error creating virtual environment: {str(e)}")
            raise BackendExceptions("Failed to create venv with PDM")
        except OSError as e:
            debug_log(f"System error creating virtual environment: {e}", "error")
            handle_exception(e, f"Error creating virtual environment: {str(e)}")
            raise BackendExceptions(f"Failed to create venv with PDM: {str(e)}")

    def install_dependencies(self, venv_path: str) -> None:
        """
        Install dependencies using PDM.

        :param venv_path: Path to the virtual environment
        :raises: BackendExceptions if dependency installation fails
        """
        try:
            if not os.path.exists(venv_path):
                debug_log(
                    "Virtual environment does not exist. Creating it first.", "warning"
                )
                print_error("Virtual environment does not exist. Creating it first.")
                venv_path = self.create_virtual_environment()
                if not venv_path:
                    raise BackendExceptions("Failed to create venv")

            pyproject_path = self.get_dependency_file_path()
            if not pyproject_path.exists():
                debug_log(f"pyproject.toml file not found at {pyproject_path}", "error")
                print_error(f"pyproject.toml file not found at {pyproject_path}")
                raise BackendExceptions("pyproject.toml file not found")

            # Install dependencies using PDM
            with console.status("[bold green]Installing dependencies with PDM..."):
                subprocess.run(
                    ["pdm", "install"],
                    cwd=str(self.project_dir),
                    check=True,
                    capture_output=True,
                    text=True,
                )

            debug_log("Dependencies installed successfully with PDM", "info")
            print_success("Dependencies installed successfully with PDM")

        except subprocess.CalledProcessError as e:
            debug_log(f"Error during dependency installation: {e.stderr}", "error")
            handle_exception(e, f"Error during dependency installation: {str(e)}")
            if hasattr(e, "stderr"):
                print_error(f"Error details: {e.stderr}")
            raise BackendExceptions("Failed to install dependencies with PDM")
        except OSError as e:
            debug_log(f"System error during dependency installation: {e}", "error")
            handle_exception(e, f"Error during dependency installation: {str(e)}")
            raise BackendExceptions(
                f"Failed to install dependencies with PDM: {str(e)}"
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
            # Create dependencies list as TOML format
            deps_toml = "[\n"
            for dep in dependencies:
                deps_toml += f'    "{dep}",\n'
            deps_toml += "]"

            # Create basic pyproject.toml content as string
            pyproject_content = f"""[project]
name = "{project_name or 'fastapi-project'}"
version = "0.1.0"
description = "{description or 'A FastAPI project'}"
authors = [
    {{name = "{author or 'Author'}", email = "{author_email or 'author@example.com'}"}},
]
dependencies = {deps_toml}
requires-python = ">=3.8"
readme = "README.md"
license = {{text = "MIT"}}

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"

[tool.hatch.build.targets.wheel]
packages = ["src"]

[tool.pdm]
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
        Add a new dependency using PDM.

        :param dependency: Dependency specification
        :param dev: Whether this is a development dependency
        """
        try:
            # Use PDM's add command to add dependency
            cmd = ["pdm", "add"]
            if dev:
                cmd.append("--dev")
            cmd.append(dependency)

            subprocess.run(
                cmd,
                cwd=str(self.project_dir),
                check=True,
                capture_output=True,
                text=True,
            )

            debug_log(
                f"Added {'dev ' if dev else ''}dependency '{dependency}' with PDM",
                "info",
            )

        except subprocess.CalledProcessError as e:
            debug_log(f"Error adding dependency with PDM: {e}", "error")
            raise BackendExceptions(f"Failed to add dependency with PDM: {str(e)}")
        except OSError as e:
            debug_log(f"System error adding dependency with PDM: {e}", "error")
            raise BackendExceptions(f"Failed to add dependency with PDM: {str(e)}")

    def initialize_project(
        self, project_name: str, author: str, author_email: str, description: str
    ) -> None:
        """
        Initialize a new PDM project with metadata.

        :param project_name: Name of the project
        :param author: Author name
        :param author_email: Author email
        :param description: Project description
        """
        try:
            # Use PDM init command for interactive setup
            subprocess.run(
                ["pdm", "init", "--non-interactive"],
                cwd=str(self.project_dir),
                check=True,
                capture_output=True,
                text=True,
            )

            # Create or update pyproject.toml with provided metadata
            pyproject_path = self.get_dependency_file_path()

            # Create basic pyproject.toml with project metadata
            pyproject_content = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "{description}"
authors = [
    {{name = "{author}", email = "{author_email}"}},
]
dependencies = []
requires-python = ">=3.8"
readme = "README.md"
license = {{text = "MIT"}}

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"

[tool.hatch.build.targets.wheel]
packages = ["src"]

[tool.pdm]
"""

            with open(pyproject_path, "w", encoding="utf-8") as f:
                f.write(pyproject_content)

            debug_log(f"Initialized PDM project: {project_name}", "info")

        except subprocess.CalledProcessError as e:
            debug_log(f"Error initializing PDM project: {e}", "error")
            raise BackendExceptions(f"Failed to initialize PDM project: {str(e)}")
        except (OSError, UnicodeEncodeError) as e:
            debug_log(f"Error updating project metadata: {e}", "error")
            raise BackendExceptions(f"Failed to update project metadata: {str(e)}")
