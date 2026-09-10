# --------------------------------------------------------------------------
# Static analysis of the generated project.
#
# The compile check is mandatory - a template that cannot be compiled is
# broken beyond argument. It is performed in-process with ``compile()`` and
# deliberately writes nothing to disk: a Docker test run beforehand can leave
# root-owned ``__pycache__`` directories in the bind-mounted project, and
# ``compileall`` would then fail with a PermissionError that says nothing
# about the template. ``mypy`` is opt-in because it needs the template's own
# dependencies installed and is far slower.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
import subprocess
import sys
from typing import List

from fastapi_fastkit.utils.logging import debug_log

from .context import InspectionContext

MYPY_TIMEOUT = 300

#: Directories never worth compiling - third party code and build artefacts.
EXCLUDED_DIRS = {".venv", "venv", "__pycache__", "node_modules"}


def _interpreter(ctx: InspectionContext) -> str:
    """Prefer the inspection venv interpreter, falling back to the host one."""
    return ctx.python_executable() or sys.executable


def _iter_python_files(root: str) -> List[str]:
    """Collect every ``.py`` file below ``root``, skipping excluded directories."""
    python_files: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        for file_name in sorted(filenames):
            if file_name.endswith(".py"):
                python_files.append(os.path.join(dirpath, file_name))
    return python_files


def check_compileall(ctx: InspectionContext) -> bool:
    """Compile every Python file of the generated project, in memory.

    Nothing is written to disk - no ``__pycache__`` is created - so the check
    stays a pure syntax gate that cannot trip over file ownership left behind
    by a containerised test run.
    """
    failures: List[str] = []

    for path in _iter_python_files(ctx.temp_dir):
        try:
            with open(path, "rb") as f:
                source = f.read()
        except OSError as e:
            failures.append(f"{path}: could not be read ({e})")
            continue

        try:
            compile(source, path, "exec", dont_inherit=True)
        except (SyntaxError, ValueError) as e:
            failures.append(f"{path}: {e}")

    if failures:
        detail = "\n".join(failures)
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
