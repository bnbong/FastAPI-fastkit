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
        Returns the root directory of the FastAPI-fastkit project by navigating up
        the file structure. This method dynamically finds the root.
        """
        return Path(__file__).parent.parent.parent.parent

    @classmethod
    def __init__(cls) -> None:
        """
        Initialize the configuration by performing important checks and setups.
        Override directories to correct position.
        """
        cls.FASTKIT_PROJECT_ROOT = str(cls.__get_fastapi_fastkit_root())
        cls.FASTKIT_TEMPLATE_ROOT = os.path.join(
            cls.FASTKIT_PROJECT_ROOT, "fastapi-project-template"
        )
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

        if not cls.LOG_FILE_PATH or not os.path.isdir(cls.FASTKIT_PROJECT_ROOT):
            raise BackendExceptions(
                "LOG_FILE_PATH is not allocated to valid directory."
            )
