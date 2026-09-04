# --------------------------------------------------------------------------
# Dependency freshness reporting.
#
# Each pinned dependency is compared against the latest release published on
# PyPI. Findings are warnings only - a template lagging behind upstream is
# worth surfacing but never a reason to fail an inspection. Network failures
# are skipped silently, and ``--offline`` disables the lookups entirely.
#
# @author bnbong
# --------------------------------------------------------------------------
import json
import re
import tomllib
import urllib.error
import urllib.request
from typing import Dict, Optional, Tuple

from fastapi_fastkit.backend.package_managers.poetry_manager import (
    _parse_pip_requirement,
)
from fastapi_fastkit.utils.logging import debug_log

from .context import InspectionContext

PYPI_JSON_URL = "https://pypi.org/pypi/{package}/json"
PYPI_TIMEOUT = 5
_VERSION_RE = re.compile(r"(\d+)\.(\d+)")
#: Only exact/lower-bound pins carry a meaningful "current version".
_PIN_OPERATORS = ("==", ">=", "~=")


def _pinned_version(requirement: str) -> Tuple[str, str]:
    """Return ``(package name, pinned version)`` for a requirement string.

    Version is empty when the requirement is unpinned or uses an operator
    that does not identify a concrete current version (e.g. ``<2``).
    """
    name, _extras, version_spec, _marker = _parse_pip_requirement(requirement)
    if not name or not version_spec:
        return name.lower() if name else "", ""
    for operator in _PIN_OPERATORS:
        if version_spec.startswith(operator):
            return name.lower(), version_spec[len(operator) :].strip()
    return name.lower(), ""


def _parse_version(version: str) -> Optional[Tuple[int, int]]:
    """Extract a (major, minor) pair from a version string."""
    match = _VERSION_RE.match(version.strip())
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def fetch_latest_version(package: str) -> Optional[str]:
    """Return the latest version of ``package`` on PyPI, or ``None`` on failure."""
    url = PYPI_JSON_URL.format(package=package)
    try:
        with urllib.request.urlopen(url, timeout=PYPI_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError, TimeoutError) as e:
        debug_log(f"PyPI lookup failed for {package}: {e}", "debug")
        return None
    version = payload.get("info", {}).get("version")
    return str(version) if version else None


def _collect_pins(ctx: InspectionContext) -> Dict[str, str]:
    """Map package name -> pinned version from the template's metadata files."""
    pins: Dict[str, str] = {}

    requirements_path = ctx.template_path / "requirements.txt-tpl"
    if requirements_path.exists():
        try:
            with open(requirements_path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except (OSError, UnicodeDecodeError):
            lines = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name, version = _pinned_version(line)
            if name and version:
                pins.setdefault(name, version)

    pyproject_path = ctx.template_path / "pyproject.toml-tpl"
    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
        except (OSError, ValueError):
            data = {}
        for dep in data.get("project", {}).get("dependencies", []) or []:
            if not isinstance(dep, str):
                continue
            name, version = _pinned_version(dep)
            if name and version:
                pins.setdefault(name, version)

    return pins


def check_dependency_freshness(ctx: InspectionContext) -> bool:
    """Warn about dependencies that lag behind their latest PyPI release.

    Always returns ``True``: freshness is advisory.
    """
    if ctx.options.offline:
        debug_log("Offline mode - skipping dependency freshness check", "info")
        return True

    pins = _collect_pins(ctx)
    if not pins:
        debug_log("No pinned dependencies found for freshness check", "info")
        return True

    checked = 0
    for package, pinned in sorted(pins.items()):
        latest = fetch_latest_version(package)
        if latest is None:
            continue
        checked += 1
        current_parts = _parse_version(pinned)
        latest_parts = _parse_version(latest)
        if current_parts is None or latest_parts is None:
            continue
        if latest_parts[0] > current_parts[0]:
            ctx.add_warning(
                f"{package} is {latest_parts[0] - current_parts[0]} major "
                f"version(s) behind: pinned {pinned}, latest {latest}"
            )
        elif latest_parts[0] == current_parts[0] and latest_parts[1] > current_parts[1]:
            ctx.add_warning(
                f"{package} is {latest_parts[1] - current_parts[1]} minor "
                f"version(s) behind: pinned {pinned}, latest {latest}"
            )

    if checked == 0:
        debug_log(
            "Dependency freshness check skipped - no PyPI responses received", "info"
        )
    else:
        debug_log(f"Dependency freshness check completed ({checked} packages)", "info")
    return True
