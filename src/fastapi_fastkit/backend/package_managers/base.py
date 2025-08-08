# --------------------------------------------------------------------------
# Base Package Manager - Abstract class for package manager implementations
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


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
        }
        default_kwargs.update(kwargs)

        return subprocess.run(command, **default_kwargs)

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
