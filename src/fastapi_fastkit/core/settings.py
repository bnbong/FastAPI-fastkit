# --------------------------------------------------------------------------
# The Module defines fastapi-fastkit project's general Env settings.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from pathlib import Path

from .exceptions import BackendExceptions


class FastkitConfig:
    # Overridable values
    FASTKIT_PROJECT_ROOT: str = ""  # default : None (will be overridden)
    FASTKIT_TEMPLATE_ROOT: str = ""  # default : None (will be overridden)
    LOG_FILE_PATH: str = ""  # default : None (will be overridden)
    USER_WORKSPACE: str = ""  # default : None (will be overridden)

    # Default Options
    DEBUG_MODE: bool = False
    LOGGING_LEVEL: str = "DEBUG"

    # Testing Options
    TEST_SERVER_PORT: int = 8000
    TEST_DEFAULT_TERMINAL_WIDTH: int = 80
    TEST_MAX_TERMINAL_WIDTH: int = 1000

    def set_debug_mode(self, debug_mode: bool = True) -> None:
        self.DEBUG_MODE = debug_mode

    @staticmethod
    def __get_fastapi_fastkit_root() -> Path:
        """
        Returns the root directory of the installed FastAPI-fastkit package.
        For development: returns the project root
        For installed package: returns the package installation directory
        """
        try:
            import fastapi_fastkit

            package_root = Path(fastapi_fastkit.__file__).parent.parent
            if package_root.name == "site-packages":
                return package_root / "fastapi_fastkit"
            return package_root
        except ImportError:
            # Fallback for development environment
            return Path(__file__).parent.parent.parent.parent

    @staticmethod
    def __get_template_root() -> Path:
        """
        Returns the template directory of the installed FastAPI-fastkit package.
        For development: returns the project template directory
        For installed package: returns the package template directory
        """
        try:
            import fastapi_fastkit

            package_root = Path(fastapi_fastkit.__file__).parent
            template_dir = package_root / "fastapi_project_template"
            if template_dir.exists():
                return template_dir
            # If inside site-packages
            if package_root.parent.name == "site-packages":
                return (
                    package_root.parent / "fastapi_fastkit" / "fastapi_project_template"
                )
            return package_root.parent / "fastapi_project_template"
        except ImportError:
            # Fallback for development environment
            return Path(__file__).parent.parent / "fastapi_project_template"

    @classmethod
    def __init__(cls) -> None:
        """
        Initialize the configuration by performing important checks and setups.
        Override directories to correct position.
        """
        cls.FASTKIT_PROJECT_ROOT = str(cls.__get_fastapi_fastkit_root())
        cls.FASTKIT_TEMPLATE_ROOT = str(cls.__get_template_root())
        cls.LOG_FILE_PATH = os.path.join(
            cls.FASTKIT_PROJECT_ROOT, "logs", "fastkit.log"
        )
        cls.USER_WORKSPACE = os.getcwd()

        # Validate the configurations
        cls._validate()

    @classmethod
    def _validate(cls) -> None:
        """
        Validate the configuration settings to ensure that they are correct.
        Raises an error if validation fails.
        """
        if not cls.FASTKIT_PROJECT_ROOT or not os.path.isdir(cls.FASTKIT_PROJECT_ROOT):
            raise BackendExceptions(
                "FASTKIT_PROJECT_ROOT is not allocated to valid directory."
            )

        if not cls.FASTKIT_TEMPLATE_ROOT or not os.path.isdir(cls.FASTKIT_PROJECT_ROOT):
            raise BackendExceptions(
                "FASTKIT_TEMPLATE_ROOT is not allocated to valid directory."
            )

        log_dir = os.path.dirname(cls.LOG_FILE_PATH)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
