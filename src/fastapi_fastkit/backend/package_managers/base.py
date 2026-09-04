# --------------------------------------------------------------------------
# Base Package Manager - Abstract class for package manager implementations
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi_fastkit.core.exceptions import BackendExceptions
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.logging import debug_log
from fastapi_fastkit.utils.main import console, handle_exception, print_error


def _with_stderr_tail(message: str, stderr: str, max_lines: int = 5) -> str:
    """Append the last few non-empty stderr lines to an error message.

    :param message: Base error message
    :param stderr: Captured stderr of the failed command
    :param max_lines: Maximum number of trailing stderr lines to include
    :return: ``message`` unchanged when stderr carries nothing useful
    """
    lines = [line.strip() for line in (stderr or "").splitlines()]
    lines = [line for line in lines if line]
    if not lines:
        return message
    return f"{message}: " + " | ".join(lines[-max_lines:])


class BasePackageManager(ABC):
    """
    Abstract base class for package managers.

    All package manager implementations must inherit from this class
    and implement the required abstract methods.
    """

    def __init__(self, project_dir: str):
        """
        Initialize package manager for a specific project.

        :param project_dir: Path to the project directory
        """
        self.project_dir = Path(project_dir)
        self.name = self.__class__.__name__.replace("Manager", "").lower()

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the package manager is available on the system.

        :return: True if package manager is installed and available
        """
        pass

    @abstractmethod
    def get_dependency_file_name(self) -> str:
        """
        Get the name of the dependency file for this package manager.

        :return: Dependency file name (e.g., 'requirements.txt', 'pyproject.toml')
        """
        pass

    @abstractmethod
    def create_virtual_environment(self) -> str:
        """
        Create a virtual environment for the project.

        :return: Path to the created virtual environment
        :raises: Exception if virtual environment creation fails
        """
        pass

    @abstractmethod
    def install_dependencies(self, venv_path: str) -> None:
        """
        Install dependencies using the package manager.

        :param venv_path: Path to the virtual environment
        :raises: Exception if dependency installation fails
        """
        pass

    @abstractmethod
    def generate_dependency_file(
        self,
        dependencies: List[str],
        project_name: str = "",
        author: str = "",
        author_email: str = "",
        description: str = "",
    ) -> None:
        """
        Generate a dependency file with the given dependencies and metadata.

        :param dependencies: List of dependency specifications
        :param project_name: Name of the project
        :param author: Author name
        :param author_email: Author email
        :param description: Project description
        """
        pass

    @abstractmethod
    def add_dependency(self, dependency: str, dev: bool = False) -> None:
        """
        Add a new dependency to the project.

        :param dependency: Dependency specification
        :param dev: Whether this is a development dependency
        """
        pass

    def get_executable_path(
        self, executable_name: str, venv_path: Optional[str] = None
    ) -> str:
        """
        Get the full path to an executable, considering virtual environment.

        :param executable_name: Name of the executable
        :param venv_path: Path to virtual environment (optional)
        :return: Full path to the executable
        """
        import os

        if venv_path:
            if os.name == "nt":  # Windows
                return os.path.join(venv_path, "Scripts", f"{executable_name}.exe")
            else:  # Unix-based
                return os.path.join(venv_path, "bin", executable_name)
        else:
            return executable_name

    def run_command(
        self, command: List[str], **kwargs: Any
    ) -> subprocess.CompletedProcess[str]:
        """
        Run a command with proper error handling.

        :param command: Command to run as list of strings
        :param kwargs: Additional keyword arguments for subprocess.run
        :return: CompletedProcess instance
        :raises: subprocess.CalledProcessError on failure
        """
        default_kwargs: Dict[str, Any] = {
            "check": True,
            "capture_output": True,
            "text": True,
            "cwd": str(self.project_dir),
            "timeout": settings.get_subprocess_timeout(),
        }
        default_kwargs.update(kwargs)

        return subprocess.run(command, **default_kwargs)

    def _check_command_available(self, command: List[str]) -> bool:
        """
        Check whether a command can be executed on the current system.

        :param command: Version probe command (e.g. ``["uv", "--version"]``)
        :return: True if the command executed successfully
        """
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=settings.get_subprocess_timeout("check"),
            )
            return True
        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
            OSError,
        ):
            return False

    def _run_checked(
        self,
        command: List[str],
        status_msg: str,
        error_prefix: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        summarize_output: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        """
        Run a command with a status spinner and uniform error handling.

        :param command: Command to run as list of strings
        :param status_msg: Message shown while the command runs
        :param error_prefix: Message used for the raised ``BackendExceptions``
        :param cwd: Working directory (defaults to the project directory)
        :param timeout: Timeout in seconds (defaults to the general timeout)
        :param summarize_output: Print the tail of the command output on success
        :return: CompletedProcess instance
        :raises BackendExceptions: if the command fails, times out or cannot run
        """
        timeout = timeout if timeout is not None else settings.get_subprocess_timeout()

        try:
            with console.status(f"[bold green]{status_msg}"):
                result: subprocess.CompletedProcess[str] = subprocess.run(
                    command,
                    cwd=cwd if cwd is not None else str(self.project_dir),
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

            if summarize_output:
                self._print_output_summary(result)

            return result

        except subprocess.TimeoutExpired as e:
            message = (
                f"{error_prefix}: command timed out after {timeout}s "
                f"({' '.join(command)}). "
                f"Set {settings.SUBPROCESS_TIMEOUT_ENV_VAR} to raise the limit."
            )
            debug_log(message, "error")
            handle_exception(e, message)
            raise BackendExceptions(message)
        except subprocess.CalledProcessError as e:
            stderr = e.stderr if isinstance(e.stderr, str) else ""
            debug_log(f"{error_prefix}: {stderr or e}", "error")
            handle_exception(e, f"{error_prefix}: {str(e)}")
            if stderr:
                print_error(f"Error details: {stderr}")
            # Carry the tail of stderr into the exception message: the raised
            # BackendExceptions is what callers (and the CLI) surface, and a
            # bare prefix leaves "why did it fail?" unanswerable from a log.
            raise BackendExceptions(_with_stderr_tail(error_prefix, stderr))
        except OSError as e:
            debug_log(f"{error_prefix}: {e}", "error")
            handle_exception(e, f"{error_prefix}: {str(e)}")
            raise BackendExceptions(f"{error_prefix}: {str(e)}")

    @staticmethod
    def _print_output_summary(
        result: subprocess.CompletedProcess[str], max_lines: int = 5
    ) -> None:
        """
        Print the tail of a completed command's output.

        Keeps the user informed about long running installs without dumping the
        whole log. Silently does nothing when there is no textual output.

        :param result: Completed process whose output should be summarized
        :param max_lines: Maximum number of trailing lines to print
        """
        chunks = [
            chunk
            for chunk in (
                getattr(result, "stdout", None),
                getattr(result, "stderr", None),
            )
            if isinstance(chunk, str)
        ]
        lines = [line.strip() for chunk in chunks for line in chunk.splitlines()]
        lines = [line for line in lines if line]
        if not lines:
            return

        for line in lines[-max_lines:]:
            console.print(f"[dim]  {line}[/dim]")

    def _ensure_venv(self, venv_path: str) -> str:
        """
        Make sure a virtual environment exists, creating it when missing.

        :param venv_path: Path to the virtual environment
        :return: Path to an existing virtual environment
        :raises BackendExceptions: if the virtual environment cannot be created
        """
        if os.path.exists(venv_path):
            return venv_path

        debug_log("Virtual environment does not exist. Creating it first.", "warning")
        print_error("Virtual environment does not exist. Creating it first.")
        created = self.create_virtual_environment()
        if not created:
            raise BackendExceptions("Failed to create venv")
        return created

    def _require_dependency_file(self, error_message: Optional[str] = None) -> Path:
        """
        Return the dependency file path, failing when it is missing.

        :param error_message: Message used for the raised exception
        :return: Path to the dependency file
        :raises BackendExceptions: if the dependency file does not exist
        """
        dependency_path = self.get_dependency_file_path()
        if not dependency_path.exists():
            file_name = self.get_dependency_file_name()
            debug_log(f"{file_name} file not found at {dependency_path}", "error")
            print_error(f"{file_name} file not found at {dependency_path}")
            raise BackendExceptions(error_message or f"{file_name} file not found")
        return dependency_path

    def get_dependency_file_path(self) -> Path:
        """
        Get the full path to the dependency file.

        :return: Path to the dependency file
        """
        return self.project_dir / self.get_dependency_file_name()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.project_dir})"

    def __repr__(self) -> str:
        return self.__str__()
