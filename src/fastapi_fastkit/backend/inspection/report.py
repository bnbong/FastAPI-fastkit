# --------------------------------------------------------------------------
# Inspection reporting: turn an InspectionContext into the report dictionary
# consumed by the CLI, the local scripts and the CI workflows.
#
# @author bnbong
# --------------------------------------------------------------------------
from typing import Any, Dict

from fastapi_fastkit.utils.logging import debug_log
from fastapi_fastkit.utils.main import print_error, print_success, print_warning

from .context import InspectionContext


def build_report(ctx: InspectionContext) -> Dict[str, Any]:
    """Build the inspection report and log a summary of the findings."""
    is_valid = len(ctx.errors) == 0
    template_name = ctx.template_path.name

    if is_valid:
        debug_log(
            f"Template inspection completed successfully for {template_name}", "info"
        )
    else:
        debug_log(
            f"Template inspection failed for {template_name} "
            f"with {len(ctx.errors)} errors",
            "error",
        )
        for index, error in enumerate(ctx.errors, 1):
            debug_log(f"Error {index}: {error}", "error")

    if ctx.warnings:
        debug_log(
            f"Template {template_name} has {len(ctx.warnings)} warnings: "
            f"{ctx.warnings}",
            "warning",
        )

    return {
        "template_path": str(ctx.template_path),
        "errors": list(ctx.errors),
        "warnings": list(ctx.warnings),
        "is_valid": is_valid,
    }


def print_report(ctx: InspectionContext, is_valid: bool) -> None:
    """Print the human-facing inspection outcome."""
    if is_valid:
        print_success(f"Template {ctx.template_path} is valid!")
    else:
        print_error(f"Template {ctx.template_path} validation failed")
        for error in ctx.errors:
            print_error(f"  - {error}")

    for warning in ctx.warnings:
        print_warning(f"  - {warning}")
