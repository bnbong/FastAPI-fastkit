# --------------------------------------------------------------------------
# The Module defines exceptions that occurs from CLI operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
class CLIExceptions(Exception):
    """
    Exceptions occurs from CLI operations
    """

    pass


class TemplateExceptions(Exception):
    """
    Exceptions occurs from deploying FastAPI templates
    """

    pass


class BackendExceptions(Exception):
    """
    Exceptions occurs from fastkit backend
    """

    pass
