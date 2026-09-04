# --------------------------------------------------------------------------
# Configuration consistency checks for a template's metadata files.
#
# FastAPI-fastkit pins generated projects to Python 3.12, so every tool that
# carries a Python version must agree. The dependency drift check keeps
# ``pyproject.toml-tpl`` and ``requirements.txt-tpl`` from diverging, and the
# self-dependency check keeps fastkit itself out of generated runtimes.
#
# @author bnbong
# --------------------------------------------------------------------------
import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi_fastkit.utils.logging import debug_log

from .checks import extract_pyproject_dependency_names, parse_requirements_names
from .context import InspectionContext

TARGET_PYTHON = "3.12"
TARGET_PYTHON_TAG = "py312"
#: fastkit is a scaffolding tool - a generated project must not depend on it.
SELF_PACKAGE_NAME = "fastapi-fastkit"


def _load_pyproject(pyproject_path: Path) -> Optional[Dict[str, Any]]:
    """Load a pyproject template file, returning ``None`` when unreadable."""
    try:
        with open(pyproject_path, "rb") as f:
            data: Dict[str, Any] = tomllib.load(f)
        return data
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        debug_log(f"Failed to parse {pyproject_path}: {e}", "warning")
        return None


def _check_python_versions(ctx: InspectionContext, data: Dict[str, Any]) -> bool:
    """requires-python / black target-version / mypy python_version must be 3.12."""
    passed = True
    tools = data.get("tool", {})

    requires_python = data.get("project", {}).get("requires-python")
    if requires_python is None:
        ctx.add_error("pyproject.toml-tpl is missing [project].requires-python")
        passed = False
    elif TARGET_PYTHON not in str(requires_python):
        ctx.add_error(
            f"requires-python must target Python {TARGET_PYTHON}, "
            f"found {requires_python!r}"
        )
        passed = False

    black_target = tools.get("black", {}).get("target-version")
    if black_target is not None:
        targets = black_target if isinstance(black_target, list) else [black_target]
        if TARGET_PYTHON_TAG not in targets:
            ctx.add_error(
                f"[tool.black].target-version must include {TARGET_PYTHON_TAG!r}, "
                f"found {black_target!r}"
            )
            passed = False

    mypy_version = tools.get("mypy", {}).get("python_version")
    if mypy_version is not None and str(mypy_version) != TARGET_PYTHON:
        ctx.add_error(
            f"[tool.mypy].python_version must be {TARGET_PYTHON!r}, "
            f"found {mypy_version!r}"
        )
        passed = False

    return passed


def _check_self_dependency(ctx: InspectionContext, names: set[str]) -> bool:
    """Generated projects must not ship FastAPI-fastkit as a runtime dependency."""
    if SELF_PACKAGE_NAME in {name.lower() for name in names}:
        ctx.add_error(
            "FastAPI-fastkit must not be a runtime dependency of a generated "
            "project (remove it from the template's dependency list)"
        )
        return False
    return True


def check_configuration_consistency(ctx: InspectionContext) -> bool:
    """Validate Python-version pins, dependency drift and self-dependency."""
    pyproject_path = ctx.template_path / "pyproject.toml-tpl"
    requirements_path = ctx.template_path / "requirements.txt-tpl"
    passed = True

    pyproject_deps: set[str] = set()
    if pyproject_path.exists():
        data = _load_pyproject(pyproject_path)
        if data is None:
            ctx.add_error("Invalid pyproject.toml-tpl: could not be parsed")
            return False
        passed = _check_python_versions(ctx, data) and passed

        pyproject_deps, parse_error = extract_pyproject_dependency_names(pyproject_path)
        if parse_error is not None:
            ctx.add_error(parse_error)
            return False
        passed = _check_self_dependency(ctx, pyproject_deps) and passed

    requirement_names: set[str] = set()
    if requirements_path.exists():
        try:
            requirement_names = parse_requirements_names(requirements_path)
        except (OSError, UnicodeDecodeError) as e:
            ctx.add_error(f"Error reading requirements.txt-tpl: {e}")
            return False
        passed = _check_self_dependency(ctx, requirement_names) and passed

    if pyproject_deps and requirement_names:
        missing: List[str] = sorted(pyproject_deps - requirement_names)
        if missing:
            ctx.add_error(
                "Dependency drift: declared in pyproject.toml-tpl but absent from "
                "requirements.txt-tpl: " + ", ".join(missing)
            )
            passed = False

    if passed:
        debug_log("Configuration consistency check passed", "info")
    return passed
