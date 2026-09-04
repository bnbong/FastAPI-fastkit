# --------------------------------------------------------------------------
# UV Package Manager Implementation
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import subprocess
from typing import List

from fastapi_fastkit.core.exceptions import BackendExceptions
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.logging import debug_log, get_logger
from fastapi_fastkit.utils.main import print_success

from .base import BasePackageManager

logger = get_logger(__name__)


class UvManager(BasePackageManager):
    """UV package manager implementation."""

    def is_available(self) -> bool:
        """Check if UV is available on the system."""
        return self._check_command_available(["uv", "--version"])

    def get_dependency_file_name(self) -> str:
        """Get the dependency file name for UV."""
        return "pyproject.toml"

    def create_virtual_environment(self) -> str:
        """
        Create a virtual environment using UV.

        :return: Path to the virtual environment
        :raises: BackendExceptions if virtual environment creation fails
        """
        venv_path = str(self.project_dir / ".venv")

        self._run_checked(
            ["uv", "venv", venv_path],
            status_msg="Creating virtual environment with UV...",
            error_prefix="Failed to create venv with UV",
            timeout=settings.get_subprocess_timeout("venv"),
        )

        debug_log(f"Virtual environment created at {venv_path}", "info")
        print_success("Virtual environment created successfully with UV")
        return venv_path

    def install_dependencies(self, venv_path: str) -> None:
        """
        Install dependencies using UV.

        :param venv_path: Path to the virtual environment
        :raises: BackendExceptions if dependency installation fails
        """
        venv_path = self._ensure_venv(venv_path)
        self._require_dependency_file()

        # Install dependencies using UV sync (including dev dependencies)
        cmd = ["uv", "sync", "--group", "dev"]
        debug_log(f"Running UV command: {' '.join(cmd)} in {self.project_dir}", "info")

        self._run_checked(
            cmd,
            status_msg="Installing dependencies with UV...",
            error_prefix="Failed to install dependencies with UV",
            timeout=settings.get_subprocess_timeout("install"),
            summarize_output=True,
        )

        debug_log("Dependencies installed successfully with UV", "info")
        print_success("Dependencies installed successfully with UV")

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

            # Create basic pyproject.toml content for UV
            pyproject_content = f"""[project]
name = "{project_name or "fastapi-project"}"
version = "0.1.0"
description = "{description or "A FastAPI project"}"
authors = [
    {{name = "{author or "Author"}", email = "{author_email or "author@example.com"}"}},
]
dependencies = {deps_toml}
requires-python = ">=3.8"
readme = "README.md"
license = {{text = "MIT"}}

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]

[tool.uv]
dev-dependencies = []
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
        Add a new dependency using UV.

        :param dependency: Dependency specification
        :param dev: Whether this is a development dependency
        """
        try:
            # Use UV's add command to add dependency
            cmd = ["uv", "add"]
            if dev:
                cmd.append("--dev")
            cmd.append(dependency)

            subprocess.run(
                cmd,
                cwd=str(self.project_dir),
                check=True,
                capture_output=True,
                text=True,
                timeout=settings.get_subprocess_timeout("install"),
            )

            debug_log(
                f"Added {'dev ' if dev else ''}dependency '{dependency}' with UV",
                "info",
            )

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            debug_log(f"Error adding dependency with UV: {e}", "error")
            raise BackendExceptions(f"Failed to add dependency with UV: {str(e)}")
        except OSError as e:
            debug_log(f"System error adding dependency with UV: {e}", "error")
            raise BackendExceptions(f"Failed to add dependency with UV: {str(e)}")

    def initialize_project(
        self, project_name: str, author: str, author_email: str, description: str
    ) -> None:
        """
        Initialize a new UV project with metadata.

        :param project_name: Name of the project
        :param author: Author name
        :param author_email: Author email
        :param description: Project description
        """
        try:
            # Use UV init command to initialize project
            subprocess.run(
                ["uv", "init", "--name", project_name],
                cwd=str(self.project_dir),
                check=True,
                capture_output=True,
                text=True,
                timeout=settings.get_subprocess_timeout(),
            )

            # Create custom pyproject.toml with provided metadata
            pyproject_path = self.get_dependency_file_path()

            # Create pyproject.toml with project metadata
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
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]

[tool.uv]
dev-dependencies = []
"""

            with open(pyproject_path, "w", encoding="utf-8") as f:
                f.write(pyproject_content)

            debug_log(f"Initialized UV project: {project_name}", "info")

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            debug_log(f"Error initializing UV project: {e}", "error")
            raise BackendExceptions(f"Failed to initialize UV project: {str(e)}")
        except (OSError, UnicodeEncodeError) as e:
            debug_log(f"Error updating project metadata: {e}", "error")
            raise BackendExceptions(f"Failed to update project metadata: {str(e)}")

    def lock_dependencies(self) -> None:
        """
        Generate UV lock file.

        :raises: BackendExceptions if lock generation fails
        """
        self._run_checked(
            ["uv", "lock"],
            status_msg="Generating UV lock file...",
            error_prefix="Failed to generate UV lock file",
            timeout=settings.get_subprocess_timeout("install"),
        )

        debug_log("UV lock file generated successfully", "info")
        print_success("UV lock file generated successfully")

    def run_script(self, script_command: str) -> None:
        """
        Run a script using UV.

        :param script_command: Command to run
        :raises: BackendExceptions if script execution fails
        """
        try:
            subprocess.run(
                ["uv", "run"] + script_command.split(),
                cwd=str(self.project_dir),
                check=True,
                capture_output=True,
                text=True,
                timeout=settings.get_subprocess_timeout(),
            )

            debug_log(f"UV script executed successfully: {script_command}", "info")

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            debug_log(f"Error running UV script: {e.stderr!r}", "error")
            raise BackendExceptions(f"Failed to run UV script: {str(e)}")
        except OSError as e:
            debug_log(f"System error running UV script: {e}", "error")
            raise BackendExceptions(f"Failed to run UV script: {str(e)}")
