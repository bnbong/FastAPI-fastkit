# --------------------------------------------------------------------------
# Package Manager Factory - Creates appropriate package manager instances
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Dict, List, Optional, Type

from fastapi_fastkit.core.exceptions import BackendExceptions
from fastapi_fastkit.utils.logging import debug_log, get_logger

from .base import BasePackageManager
from .pdm_manager import PdmManager
from .pip_manager import PipManager
from .poetry_manager import PoetryManager
from .uv_manager import UvManager

logger = get_logger(__name__)


class PackageManagerFactory:
    """Factory for creating package manager instances."""

    # Registry of available package managers
    _managers: Dict[str, Type[BasePackageManager]] = {
        "pip": PipManager,
        "pdm": PdmManager,
        "uv": UvManager,
        "poetry": PoetryManager,
    }

    @classmethod
    def create_manager(
        self, manager_type: str, project_dir: str, auto_detect: bool = False
    ) -> BasePackageManager:
        """
        Create a package manager instance.

        :param manager_type: Type of package manager ('pip', 'uv', 'pdm', 'poetry')
        :param project_dir: Path to the project directory
        :param auto_detect: If True, auto-detect available package manager when requested type is not available
        :return: Package manager instance
        :raises: BackendExceptions if manager type is not supported or not available
        """
        manager_type = manager_type.lower()

        # Check if requested manager type is supported
        if manager_type not in self._managers:
            available_managers = list(self._managers.keys())
            error_msg = f"Unsupported package manager: {manager_type}. Available: {available_managers}"
            debug_log(error_msg, "error")
            raise BackendExceptions(error_msg)

        # Create the manager instance
        manager_class = self._managers[manager_type]
        manager = manager_class(project_dir)

        # Check if the manager is available on the system
        if not manager.is_available():
            if auto_detect:
                debug_log(
                    f"{manager_type} is not available, trying to auto-detect alternative",
                    "warning",
                )
                return self._auto_detect_manager(project_dir, exclude=[manager_type])
            else:
                error_msg = (
                    f"Package manager '{manager_type}' is not available on the system"
                )
                debug_log(error_msg, "error")
                raise BackendExceptions(error_msg)

        debug_log(f"Created {manager_type} package manager for {project_dir}", "info")
        return manager

    @classmethod
    def _auto_detect_manager(
        self, project_dir: str, exclude: Optional[List[str]] = None
    ) -> BasePackageManager:
        """
        Auto-detect the best available package manager.

        :param project_dir: Path to the project directory
        :param exclude: List of manager types to exclude from detection
        :return: Package manager instance
        :raises: BackendExceptions if no package manager is available
        """
        exclude = exclude or []

        # Priority order for auto-detection
        detection_order = ["uv", "pdm", "poetry", "pip"]

        for manager_type in detection_order:
            if manager_type in exclude:
                continue

            if manager_type not in self._managers:
                continue

            manager_class = self._managers[manager_type]
            manager = manager_class(project_dir)

            if manager.is_available():
                debug_log(f"Auto-detected package manager: {manager_type}", "info")
                return manager

        error_msg = "No package manager is available on the system"
        debug_log(error_msg, "error")
        raise BackendExceptions(error_msg)

    @classmethod
    def get_available_managers(self) -> list[str]:
        """
        Get list of available package managers on the current system.

        :return: List of available package manager names
        """
        available = []

        for manager_type, manager_class in self._managers.items():
            # Create a temporary instance to check availability
            # Using current directory as a dummy project path
            temp_manager = manager_class(".")
            if temp_manager.is_available():
                available.append(manager_type)

        return available

    @classmethod
    def register_manager(
        self, name: str, manager_class: Type[BasePackageManager]
    ) -> None:
        """
        Register a new package manager type.

        :param name: Name of the package manager
        :param manager_class: Package manager class
        """
        if not issubclass(manager_class, BasePackageManager):
            raise ValueError(f"Manager class must inherit from BasePackageManager")

        self._managers[name.lower()] = manager_class
        debug_log(f"Registered package manager: {name}", "info")

    @classmethod
    def get_supported_managers(self) -> list[str]:
        """
        Get list of all supported package manager types.

        :return: List of supported package manager names
        """
        return list(self._managers.keys())
