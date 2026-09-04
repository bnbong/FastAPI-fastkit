# --------------------------------------------------------------------------
# Pip Package Manager Implementation
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import sys
from typing import List

from fastapi_fastkit.core.exceptions import BackendExceptions
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.logging import debug_log, get_logger
from fastapi_fastkit.utils.main import print_success

from .base import BasePackageManager

logger = get_logger(__name__)


class PipManager(BasePackageManager):
    """Pip package manager implementation."""

    def is_available(self) -> bool:
        """Check if pip is available on the system."""
        return self._check_command_available([sys.executable, "-m", "pip", "--version"])

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

        self._run_checked(
            [sys.executable, "-m", "venv", venv_path],
            status_msg="Creating virtual environment...",
            error_prefix="Failed to create venv",
            timeout=settings.get_subprocess_timeout("venv"),
        )

        debug_log(f"Virtual environment created at {venv_path}", "info")
        print_success("Virtual environment created successfully")
        return venv_path

    def install_dependencies(self, venv_path: str, upgrade_pip: bool = False) -> None:
        """
        Install dependencies using pip in the virtual environment.

        :param venv_path: Path to the virtual environment
        :param upgrade_pip: Upgrade pip inside the venv before installing
        :raises: BackendExceptions if dependency installation fails
        """
        venv_path = self._ensure_venv(venv_path)
        requirements_path = self._require_dependency_file("Requirements file not found")

        pip_path = self.get_executable_path("pip", venv_path)

        if upgrade_pip:
            self._run_checked(
                [pip_path, "install", "--upgrade", "pip"],
                status_msg="Upgrading pip...",
                error_prefix="Failed to upgrade pip",
                timeout=settings.get_subprocess_timeout("install"),
            )

        self._run_checked(
            [pip_path, "install", "-r", str(requirements_path.name)],
            status_msg="Installing dependencies...",
            error_prefix="Failed to install dependencies",
            timeout=settings.get_subprocess_timeout("install"),
            summarize_output=True,
        )

        debug_log("Dependencies installed successfully", "info")
        print_success("Dependencies installed successfully")

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
