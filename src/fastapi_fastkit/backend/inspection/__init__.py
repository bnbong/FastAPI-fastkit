# --------------------------------------------------------------------------
# Template inspection package.
#
# ``TemplateInspector`` generates a throwaway project from a template and runs
# the checks defined in the sibling modules against it:
#
# - ``checks``      : structure, extensions, dependencies, implementation, tests
# - ``consistency`` : Python-version pins and dependency drift
# - ``lint``        : compileall (required) and mypy (opt-in)
# - ``smoke``       : boots the generated app and probes /docs and /health
# - ``strategies``  : how the template's own test suite is executed
# - ``docker``      : Docker Compose orchestration
# - ``freshness``   : PyPI version-lag warnings
# - ``report``      : report construction and printing
#
# @author bnbong
# --------------------------------------------------------------------------
from .context import InspectionContext, InspectionOptions
from .core import TemplateInspector, inspect_fastapi_template

__all__ = [
    "InspectionContext",
    "InspectionOptions",
    "TemplateInspector",
    "inspect_fastapi_template",
]
