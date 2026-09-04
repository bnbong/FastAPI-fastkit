# --------------------------------------------------------------------------
# Shared state for the template inspection pipeline.
#
# Every check and test strategy operates on an ``InspectionContext``: it owns
# the template source path, the temporary generated-project path, the loaded
# template configuration and the accumulated errors/warnings.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi_fastkit.utils.logging import debug_log


@dataclass
class InspectionOptions:
    """Tunable switches for a single inspection run."""

    #: Skip every network access (dependency freshness lookups).
    offline: bool = False
    #: Boot the generated project with uvicorn and probe its HTTP endpoints.
    run_smoke_test: bool = True
    #: Run ``mypy`` inside the generated project (opt-in, slow).
    run_mypy: bool = False
    #: Run the template's own test suite.
    run_template_tests: bool = True
    #: Seconds to wait for the smoke-test server to answer.
    smoke_timeout: int = 60


@dataclass
class InspectionContext:
    """Mutable state shared by all inspection steps."""

    template_path: Path
    temp_dir: str
    options: InspectionOptions = field(default_factory=InspectionOptions)
    template_config: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    #: Populated by a test strategy so later checks can reuse the environment.
    venv_path: Optional[str] = None

    def add_error(self, message: str) -> None:
        """Record a fatal finding."""
        self.errors.append(message)
        debug_log(f"Inspection error: {message}", "error")

    def add_warning(self, message: str) -> None:
        """Record a non-fatal finding."""
        self.warnings.append(message)
        debug_log(f"Inspection warning: {message}", "warning")

    def temp_path(self, *parts: str) -> str:
        """Join ``parts`` onto the generated project directory."""
        return os.path.join(self.temp_dir, *parts)

    def python_executable(self) -> Optional[str]:
        """Return the interpreter of the inspection venv, if one was created."""
        if not self.venv_path:
            return None
        if os.name == "nt":  # pragma: no cover - Windows-only branch
            return os.path.join(self.venv_path, "Scripts", "python")
        return os.path.join(self.venv_path, "bin", "python")
