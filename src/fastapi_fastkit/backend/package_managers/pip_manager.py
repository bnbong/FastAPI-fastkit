# --------------------------------------------------------------------------
# Pip Package Manager Implementation
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


class PipManager(BasePackageManager):
    """Pip package manager implementation."""

    def is_available(self) -> bool:
        """Check if pip is available on the system."""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_dependency_file_name(self) -> str:
        """Get the dependency file name for pip."""
        return "requirements.txt"

    def create_virtual_environment(self) -> str:
        """
        Create a Python virtual environment using venv module.

        :return: Path to the virtual environment
        :raises: BackendExceptions if virtual environment creation fails
        """
        venv_path = str(self.project_dir / ".venv")

        try:
            with console.status("[bold green]Creating virtual environment..."):
                subprocess.run(
                    [sys.executable, "-m", "venv", venv_path],
                    check=True,
                    capture_output=True,
                    text=True,
                )

            debug_log(f"Virtual environment created at {venv_path}", "info")
            print_success("Virtual environment created successfully")
            return venv_path

        except subprocess.CalledProcessError as e:
            debug_log(f"Error creating virtual environment: {e.stderr}", "error")
            handle_exception(e, f"Error creating virtual environment: {str(e)}")
            raise BackendExceptions("Failed to create venv")
        except OSError as e:
            debug_log(f"System error creating virtual environment: {e}", "error")
            handle_exception(e, f"Error creating virtual environment: {str(e)}")
            raise BackendExceptions(f"Failed to create venv: {str(e)}")

    def install_dependencies(self, venv_path: str) -> None:
        """
        Install dependencies using pip in the virtual environment.

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

            requirements_path = self.get_dependency_file_path()
            if not requirements_path.exists():
                debug_log(
                    f"Requirements file not found at {requirements_path}", "error"
                )
                print_error(f"Requirements file not found at {requirements_path}")
                raise BackendExceptions("Requirements file not found")

            # Get pip path
            pip_path = self.get_executable_path("pip", venv_path)

            # Upgrade pip first
            subprocess.run(
                [pip_path, "install", "--upgrade", "pip"],
                check=True,
                capture_output=True,
                text=True,
            )

            # Install dependencies
            with console.status("[bold green]Installing dependencies..."):
                subprocess.run(
                    [pip_path, "install", "-r", str(requirements_path.name)],
                    cwd=str(self.project_dir),
                    check=True,
                    capture_output=True,
                    text=True,
                )

            debug_log("Dependencies installed successfully", "info")
            print_success("Dependencies installed successfully")

        except subprocess.CalledProcessError as e:
            debug_log(f"Error during dependency installation: {e.stderr}", "error")
            handle_exception(e, f"Error during dependency installation: {str(e)}")
            if hasattr(e, "stderr"):
                print_error(f"Error details: {e.stderr}")
            raise BackendExceptions("Failed to install dependencies")
        except OSError as e:
            debug_log(f"System error during dependency installation: {e}", "error")
            handle_exception(e, f"Error during dependency installation: {str(e)}")
            raise BackendExceptions(f"Failed to install dependencies: {str(e)}")

    def generate_dependency_file(
        self,
        dependencies: List[str],
        project_name: str = "",
        author: str = "",
        author_email: str = "",
        description: str = "",
    ) -> None:
        """
        Generate a requirements.txt file with the given dependencies.

        :param dependencies: List of dependency specifications
        :param project_name: Name of the project (not used for pip)
        :param author: Author name (not used for pip)
        :param author_email: Author email (not used for pip)
        :param description: Project description (not used for pip)
        """
        requirements_path = self.get_dependency_file_path()

        try:
            with open(requirements_path, "w", encoding="utf-8") as f:
                for dep in dependencies:
                    f.write(f"{dep}\n")

            debug_log(
                f"Generated {requirements_path} with {len(dependencies)} dependencies",
                "info",
            )

        except (OSError, UnicodeEncodeError) as e:
            debug_log(f"Error generating requirements.txt: {e}", "error")
            raise BackendExceptions(f"Failed to generate requirements.txt: {str(e)}")

    def add_dependency(self, dependency: str, dev: bool = False) -> None:
        """
        Add a new dependency to requirements.txt.

        Note: pip doesn't have built-in support for dev dependencies,
        so we'll add them to the main requirements.txt file.

        :param dependency: Dependency specification
        :param dev: Whether this is a development dependency (ignored for pip)
        """
        requirements_path = self.get_dependency_file_path()

        try:
            # Read existing dependencies
            existing_deps = []
            if requirements_path.exists():
                with open(requirements_path, "r", encoding="utf-8") as f:
                    existing_deps = [
                        line.strip() for line in f.readlines() if line.strip()
                    ]

            # Add new dependency if not already present
            if dependency not in existing_deps:
                existing_deps.append(dependency)

                with open(requirements_path, "w", encoding="utf-8") as f:
                    for dep in existing_deps:
                        f.write(f"{dep}\n")

                debug_log(
                    f"Added dependency '{dependency}' to requirements.txt", "info"
                )
            else:
                debug_log(
                    f"Dependency '{dependency}' already exists in requirements.txt",
                    "info",
                )

        except (OSError, UnicodeEncodeError, UnicodeDecodeError) as e:
            debug_log(f"Error adding dependency: {e}", "error")
            raise BackendExceptions(f"Failed to add dependency: {str(e)}")
