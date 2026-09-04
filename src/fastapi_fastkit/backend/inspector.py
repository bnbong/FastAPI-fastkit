# --------------------------------------------------------------------------
# Backwards-compatible facade for the template inspector.
#
# The implementation lives in ``fastapi_fastkit.backend.inspection``; this
# module keeps the historical import path (`from fastapi_fastkit.backend.
# inspector import inspect_fastapi_template`) working and doubles as the
# command line entry point.
#
# @author bnbong
# --------------------------------------------------------------------------
import sys

from fastapi_fastkit.backend.inspection import (
    InspectionContext,
    InspectionOptions,
    TemplateInspector,
    inspect_fastapi_template,
)
from fastapi_fastkit.utils.main import print_error

__all__ = [
    "InspectionContext",
    "InspectionOptions",
    "TemplateInspector",
    "inspect_fastapi_template",
]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_error("Usage: python inspector.py <template_dir>")
        sys.exit(1)

    inspect_fastapi_template(sys.argv[1])
