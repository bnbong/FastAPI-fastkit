# --------------------------------------------------------------------------
# The Module defines fastapi-fastkit project's general Env settings.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os

from pathlib import Path


class FastkitConfig:
    # Overridable values
    FASTKIT_PROJECT_ROOT: str = (
        os.getcwd()
    )  # default : current cursor(will be overridden)
    FASTKIT_TEMPLATE_ROOT: str = os.path.join(
        FASTKIT_PROJECT_ROOT, "fastapi-project-template"
    )
    LOG_FILE_PATH: str = os.path.join(FASTKIT_PROJECT_ROOT, "logs", "fastkit.log")

    # Default Options
    USER_WORKSPACE: str = os.getcwd()
    DEBUG_MODE: bool = True
    LOGGING_LEVEL: str = "DEBUG"

    # Testing Options
    TEST_SERVER_PORT: int = 8000

    @staticmethod
    def __get_fastapi_fastkit_root() -> Path:
        """
        Returns the root directory of the FastAPI-fastkit project by navigating up
        the file structure. This method dynamically finds the root.
        """
        return Path(__file__).parent.parent.parent.parent

    @classmethod
    def initialize(cls):
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


FastkitConfig.initialize()
