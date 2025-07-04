# --------------------------------------------------------------------------
# The Module defines exceptions that occurs from CLI operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------


class CLIExceptions(Exception):
    """
    Custom exception class for CLI operations.

    Raised when errors occur during CLI command execution,
    such as invalid arguments, missing files, or command failures.
    """

    pass


class TemplateExceptions(Exception):
    """
    Custom exception class for FastAPI template operations.

    Raised when errors occur during template deployment, validation,
    or file processing operations.
    """

    pass


class BackendExceptions(Exception):
    """
    Custom exception class for fastkit backend operations.

    Raised when errors occur in the backend logic, such as
    project creation, dependency installation, or file manipulation.
    """

    pass
