# --------------------------------------------------------------------------
# Static analysis of the generated project.
#
# ``compileall`` is mandatory - a template that cannot be byte-compiled is
# broken beyond argument. ``mypy`` is opt-in because it needs the template's
# own dependencies installed and is far slower.
#
# @author bnbong
# --------------------------------------------------------------------------
import subprocess
import sys
from typing import List

from fastapi_fastkit.utils.logging import debug_log

from .context import InspectionContext

COMPILE_TIMEOUT = 120
MYPY_TIMEOUT = 300


def _interpreter(ctx: InspectionContext) -> str:
    """Prefer the inspection venv interpreter, falling back to the host one."""
    return ctx.python_executable() or sys.executable


def check_compileall(ctx: InspectionContext) -> bool:
    """Byte-compile every Python file of the generated project."""
    command: List[str] = [
        _interpreter(ctx),
        "-m",
        "compileall",
        "-q",
        "-x",
        r"(\.venv|venv|node_modules)",
        ctx.temp_dir,
    ]
    try:
        result = subprocess.run(
            command,
            cwd=ctx.temp_dir,
            capture_output=True,
            text=True,
            timeout=COMPILE_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        ctx.add_error("compileall timed out")
        return False
    except OSError as e:
        ctx.add_error(f"Failed to run compileall: {e}")
        return False

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        ctx.add_error(f"Generated project failed to compile:\n{detail}")
        return False

    debug_log("compileall check passed", "info")
    return True


def check_mypy(ctx: InspectionContext) -> bool:
    """Run mypy inside the generated project (opt-in via ``--mypy``)."""
    if not ctx.options.run_mypy:
        debug_log("mypy check disabled", "info")
        return True

    try:
        result = subprocess.run(
            [_interpreter(ctx), "-m", "mypy", "."],
            cwd=ctx.temp_dir,
            capture_output=True,
            text=True,
            timeout=MYPY_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        ctx.add_error("mypy timed out")
        return False
    except OSError as e:
        ctx.add_warning(f"Could not run mypy: {e}")
        return True

    if result.returncode != 0:
        detail = (result.stdout or result.stderr or "").strip()
        ctx.add_error(f"mypy reported errors in the generated project:\n{detail}")
        return False

    debug_log("mypy check passed", "info")
    return True
