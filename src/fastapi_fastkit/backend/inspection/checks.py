# --------------------------------------------------------------------------
# Static template checks: structure, file extensions, declared dependencies,
# FastAPI implementation and the mandatory test suite.
#
# Every function takes an ``InspectionContext`` and returns ``True`` when the
# check passes, appending a descriptive message to ``ctx.errors`` otherwise.
#
# @author bnbong
# --------------------------------------------------------------------------
import ast
import os
import tomllib
from pathlib import Path
from typing import List, Optional, Set, Tuple

from fastapi_fastkit.backend.main import (
    _parse_setup_dependencies,
    find_template_core_modules,
)
from fastapi_fastkit.backend.package_managers.poetry_manager import (
    _parse_pip_requirement,
)
from fastapi_fastkit.utils.logging import debug_log

from .context import InspectionContext

ALWAYS_REQUIRED_PATHS = ["tests", "README.md-tpl"]
METADATA_CANDIDATES = ["pyproject.toml-tpl", "setup.py-tpl"]


def extract_pyproject_dependency_names(
    pyproject_path: Path,
) -> Tuple[Set[str], Optional[str]]:
    """Parse a pyproject file and return (lowercased dep names, error).

    ``error`` is ``None`` on success. Returns an empty set with a descriptive
    error string when the file is unreadable or malformed.
    """
    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        return set(), f"Invalid pyproject.toml-tpl: {e}"

    project = data.get("project", {})
    raw_deps = project.get("dependencies", []) or []
    if not isinstance(raw_deps, list):
        return set(), "pyproject.toml-tpl [project].dependencies must be a list"

    names: Set[str] = set()
    for dep in raw_deps:
        if not isinstance(dep, str) or not dep.strip():
            continue
        name = _parse_pip_requirement(dep)[0]
        if name:
            names.add(name.lower())
    return names, None


def parse_requirements_names(requirements_path: Path) -> Set[str]:
    """Return the lowercased package names declared in a requirements file."""
    with open(requirements_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return {
        _parse_pip_requirement(line)[0].lower()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    }


def check_file_structure(ctx: InspectionContext) -> bool:
    """Check the required file and directory structure.

    Modern templates may ship ``pyproject.toml-tpl`` as the primary metadata
    file; ``setup.py-tpl`` remains accepted for backward compatibility.
    A template must provide at least one of the two. ``requirements.txt-tpl``
    is no longer strictly required when ``pyproject.toml-tpl`` declares
    ``[project].dependencies``.
    """
    missing_required = [
        path
        for path in ALWAYS_REQUIRED_PATHS
        if not (ctx.template_path / path).exists()
    ]
    has_metadata = any(
        (ctx.template_path / name).exists() for name in METADATA_CANDIDATES
    )

    for path in missing_required:
        ctx.add_error(f"Missing required path: {path}")
    if not has_metadata:
        ctx.add_error(
            "Missing metadata file: expected pyproject.toml-tpl "
            "(preferred) or setup.py-tpl"
        )

    if missing_required or not has_metadata:
        return False

    debug_log("File structure check passed", "info")
    return True


def check_file_extensions(ctx: InspectionContext) -> bool:
    """Check all Python files in the template carry the .py-tpl extension."""
    for path in ctx.template_path.rglob("*"):
        if path.is_file() and path.suffix == ".py":
            ctx.add_error(f"Found .py file instead of .py-tpl: {path}")
            return False

    debug_log("File extension check passed", "info")
    return True


def check_dependencies(ctx: InspectionContext) -> bool:
    """Check that FastAPI is declared in at least one supported source.

    All three metadata sources are consulted independently:

    - ``requirements.txt-tpl``
    - ``pyproject.toml-tpl`` ``[project].dependencies``
    - ``setup.py-tpl`` ``install_requires``

    The check passes if *any* source declares ``fastapi``, so a template
    with a stale ``requirements.txt-tpl`` still passes when
    ``pyproject.toml-tpl`` is authoritative.
    """
    req_path = ctx.template_path / "requirements.txt-tpl"
    pyproject_path = ctx.template_path / "pyproject.toml-tpl"
    setup_path = ctx.template_path / "setup.py-tpl"

    sources_checked: List[str] = []
    fastapi_declared = False

    if req_path.exists():
        sources_checked.append("requirements.txt-tpl")
        try:
            package_names = parse_requirements_names(req_path)
        except (OSError, UnicodeDecodeError) as e:
            ctx.add_error(f"Error reading requirements.txt-tpl: {e}")
            return False
        debug_log(
            f"requirements.txt-tpl dependencies: {sorted(package_names)}", "debug"
        )
        fastapi_declared = fastapi_declared or "fastapi" in package_names

    if pyproject_path.exists():
        sources_checked.append("pyproject.toml-tpl")
        package_names, parse_error = extract_pyproject_dependency_names(pyproject_path)
        if parse_error is not None:
            ctx.add_error(parse_error)
            return False
        debug_log(f"pyproject.toml-tpl dependencies: {sorted(package_names)}", "debug")
        fastapi_declared = fastapi_declared or "fastapi" in package_names

    if setup_path.exists():
        sources_checked.append("setup.py-tpl")
        try:
            with open(setup_path, encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            ctx.add_error(f"Error reading setup.py-tpl: {e}")
            return False
        package_names = {
            _parse_pip_requirement(dep)[0].lower()
            for dep in _parse_setup_dependencies(content)
            if dep
        }
        debug_log(f"setup.py-tpl dependencies: {sorted(package_names)}", "debug")
        fastapi_declared = fastapi_declared or "fastapi" in package_names

    if not sources_checked:
        ctx.add_error(
            "No dependency source found: expected one of requirements.txt-tpl, "
            "pyproject.toml-tpl, or setup.py-tpl"
        )
        return False

    if not fastapi_declared:
        ctx.add_error(
            "FastAPI dependency not found in any source ("
            + ", ".join(sources_checked)
            + ")"
        )
        return False

    debug_log(
        f"Dependencies check passed (sources: {', '.join(sources_checked)})", "info"
    )
    return True


def _module_defines_fastapi_app(source: str) -> bool:
    """Return True when ``source`` assigns a ``FastAPI(...)`` instance."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value
        if not isinstance(value, ast.Call):
            continue
        func = value.func
        name = ""
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name == "FastAPI":
            return True
    return False


def check_fastapi_implementation(ctx: InspectionContext) -> bool:
    """Check the generated project really instantiates a FastAPI application.

    This is a static (AST) guard so a broken main module is reported before
    the far more expensive smoke test boots a server.
    """
    try:
        core_modules = find_template_core_modules(ctx.temp_dir)
        debug_log(f"Found core modules: {core_modules}", "debug")

        if not core_modules["main"]:
            ctx.add_error("main.py not found in template")
            return False

        with open(core_modules["main"], encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        ctx.add_error(f"Error checking FastAPI implementation: {e}")
        return False

    if not _module_defines_fastapi_app(content):
        ctx.add_error("FastAPI app creation not found in main.py")
        debug_log(f"main.py content preview: {content[:200]}...", "debug")
        return False

    debug_log("FastAPI implementation check passed", "info")
    return True


def check_tests_present(ctx: InspectionContext) -> bool:
    """A template must ship at least one test module.

    Previously a missing ``tests/`` directory only produced a warning; an
    untested template is now a hard failure.
    """
    tests_dir = ctx.template_path / "tests"
    if not tests_dir.is_dir():
        ctx.add_error("Missing required path: tests (templates must ship tests)")
        return False

    test_files = [
        path
        for path in tests_dir.rglob("*")
        if path.is_file()
        and path.name.startswith("test_")
        and path.name.endswith((".py-tpl", ".py"))
    ]
    if not test_files:
        ctx.add_error(
            "No test module found under tests/: at least one test_*.py-tpl file "
            "is required"
        )
        return False

    debug_log(f"Test suite check passed ({len(test_files)} test files)", "info")
    return True


def check_no_junk_files(ctx: InspectionContext) -> bool:
    """Reject OS/editor artifacts and build leftovers committed to a template."""
    junk_names = {".DS_Store", "Thumbs.db", "desktop.ini", ".AppleDouble"}
    junk_dirs = {"__pycache__", ".pytest_cache", ".mypy_cache", ".venv"}
    found: List[str] = []

    for path in ctx.template_path.rglob("*"):
        rel = path.relative_to(ctx.template_path)
        if path.is_dir():
            if path.name in junk_dirs:
                found.append(str(rel))
        elif path.name in junk_names or path.suffix in {".pyc", ".pyo"}:
            found.append(str(rel))

    if found:
        for item in sorted(found):
            ctx.add_error(f"Junk file committed to template: {item}")
        return False

    debug_log("Junk file check passed", "info")
    return True


def check_no_placeholder_residue(ctx: InspectionContext) -> bool:
    """Every ``<placeholder>`` must be substituted during project generation.

    The inspection generates a real project from the template (copy +
    metadata injection), so any surviving placeholder token means the
    template declares a variable the generator does not know how to fill.
    """
    placeholders = [
        "<project_name>",
        "<author>",
        "<author_email>",
        "<description>",
    ]
    text_suffixes = {
        ".py",
        ".toml",
        ".cfg",
        ".txt",
        ".md",
        ".yml",
        ".yaml",
        ".json",
        ".sh",
        ".env",
        ".ini",
    }
    residue: List[str] = []

    for root, dirs, files in os.walk(ctx.temp_dir):
        dirs[:] = [d for d in dirs if d not in {".venv", "venv", "__pycache__", ".git"}]
        for file_name in files:
            file_path = os.path.join(root, file_name)
            suffix = Path(file_name).suffix
            if suffix and suffix not in text_suffixes:
                continue
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            hits = [token for token in placeholders if token in content]
            if hits:
                rel = os.path.relpath(file_path, ctx.temp_dir)
                residue.append(f"{rel}: {', '.join(hits)}")

    if residue:
        for item in sorted(residue):
            ctx.add_error(f"Unsubstituted placeholder in generated project: {item}")
        return False

    debug_log("Placeholder substitution check passed", "info")
    return True
