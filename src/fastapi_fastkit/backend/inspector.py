# --------------------------------------------------------------------------
# The Module defines FastAPI template inspector for template validation.
# This module will be used by maintainers of FastAPI-fastkit when anyone
#   makes a PR of adding new FastAPI template.
#
# First, check a FastAPI template is formed a valid template form with .py-tpl extension
#   & dependencies requirements.
# Second, check a FastAPI template has a proper FastAPI server implementation.
#   main.py module must have a FastAPI app creation. like `app = FastAPI()`
# Third, check a FastAPI template has passed all the tests.
#
# This module create temporary named 'temp' directory at src/fastapi_fastkit/backend
#   and copy a template to Funtional FastAPI application into the temp directory.
# After the inspection, it will be deleted.
#
# This module include virtual environment creation & installation of dependencies.
# Depending on the volume in which the template is implemented and the number of dependencies,
#   it may take some time to complete the inspection.
#
# @author bnbong
# --------------------------------------------------------------------------
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from fastapi_fastkit.backend.main import (
    create_venv,
    find_template_core_modules,
    install_dependencies,
)
from fastapi_fastkit.backend.transducer import copy_and_convert_template
from fastapi_fastkit.core.settings import settings
from fastapi_fastkit.utils.logging import debug_log, get_logger
from fastapi_fastkit.utils.main import print_error, print_success, print_warning

logger = get_logger(__name__)


class TemplateInspector:
    """
    Template inspector for validating FastAPI templates.

    Uses context manager protocol for proper resource cleanup.
    """

    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        self._cleanup_needed = False

    def __enter__(self) -> "TemplateInspector":
        """Enter context manager - create temp directory and copy template."""
        try:
            os.makedirs(self.temp_dir, exist_ok=True)
            copy_and_convert_template(str(self.template_path), self.temp_dir)
            self._cleanup_needed = True
            debug_log(f"Created temporary directory at {self.temp_dir}", "debug")
            return self
        except Exception as e:
            debug_log(f"Failed to setup template inspector: {e}", "error")
            self._cleanup()
            raise

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager - cleanup temp directory."""
        self._cleanup()

    def _cleanup(self) -> None:
        """Cleanup temp directory if it exists and cleanup is needed."""
        if self._cleanup_needed and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                debug_log(f"Cleaned up temp directory {self.temp_dir}", "debug")
            except OSError as e:
                debug_log(
                    f"Failed to cleanup temp directory {self.temp_dir}: {e}", "warning"
                )
            finally:
                self._cleanup_needed = False

    def inspect_template(self) -> bool:
        """
        Inspect the template to validate it's a proper FastAPI application.

        :return: True if template is valid, False otherwise
        """
        checks: List[Tuple[str, Callable[[], bool]]] = [
            ("File Structure", self._check_file_structure),
            ("File Extensions", self._check_file_extensions),
            ("Dependencies", self._check_dependencies),
            ("FastAPI Implementation", self._check_fastapi_implementation),
            ("Template Tests", self._test_template),
        ]

        for check_name, check_func in checks:
            debug_log(f"Running check: {check_name}", "info")
            if not check_func():
                debug_log(f"Check failed: {check_name}", "error")
                return False
            debug_log(f"Check passed: {check_name}", "info")

        return True

    def _check_file_structure(self) -> bool:
        """Check the required file and directory structure."""
        required_paths = [
            "tests",
            "requirements.txt-tpl",
            "setup.py-tpl",
            "README.md-tpl",
        ]

        for path in required_paths:
            if not (self.template_path / path).exists():
                self.errors.append(f"Missing required path: {path}")
                return False
        return True

    def _check_file_extensions(self) -> bool:
        """Check all Python files have .py-tpl extension."""
        for path in self.template_path.rglob("*"):
            if path.is_file() and path.suffix == ".py":
                self.errors.append(f"Found .py file instead of .py-tpl: {path}")
                return False
        return True

    def _check_dependencies(self) -> bool:
        """Check the dependencies in both setup.py-tpl and requirements.txt-tpl."""
        req_path = self.template_path / "requirements.txt-tpl"
        setup_path = self.template_path / "setup.py-tpl"

        if not req_path.exists():
            self.errors.append("requirements.txt-tpl not found")
            return False
        if not setup_path.exists():
            self.errors.append("setup.py-tpl not found")
            return False

        try:
            with open(req_path, encoding="utf-8") as f:
                deps = f.read().splitlines()
                package_names = [dep.split("==")[0] for dep in deps if dep]
                if "fastapi" not in package_names:
                    self.errors.append(
                        "FastAPI dependency not found in requirements.txt-tpl"
                    )
                    return False
        except (OSError, UnicodeDecodeError) as e:
            self.errors.append(f"Error reading requirements.txt-tpl: {e}")
            return False
        return True

    def _check_fastapi_implementation(self) -> bool:
        """Check if the template has a proper FastAPI server implementation."""
        try:
            core_modules = find_template_core_modules(self.temp_dir)

            if not core_modules["main"]:
                self.errors.append("main.py not found in template")
                return False

            with open(core_modules["main"], encoding="utf-8") as f:
                content = f.read()
                if "FastAPI" not in content or "app" not in content:
                    self.errors.append("FastAPI app creation not found in main.py")
                    return False
        except (OSError, UnicodeDecodeError) as e:
            self.errors.append(f"Error checking FastAPI implementation: {e}")
            return False
        return True

    def _test_template(self) -> bool:
        """Run tests on the template if they exist."""
        test_dir = os.path.join(self.temp_dir, "tests")
        if not os.path.exists(test_dir):
            self.warnings.append("No tests directory found")
            return True

        try:
            # Create virtual environment for testing
            venv_path = create_venv(self.temp_dir)
            install_dependencies(self.temp_dir, venv_path)

            # Run tests
            if os.name == "nt":  # Windows
                python_executable = os.path.join(venv_path, "Scripts", "python")
            else:  # Unix-based
                python_executable = os.path.join(venv_path, "bin", "python")

            result = subprocess.run(
                [python_executable, "-m", "pytest", test_dir, "-v"],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            if result.returncode != 0:
                self.errors.append(f"Tests failed: {result.stderr}")
                return False

            debug_log("All tests passed successfully", "info")
            return True

        except subprocess.TimeoutExpired:
            self.errors.append("Tests timed out after 5 minutes")
            return False
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Error running tests: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error during testing: {e}")
            return False

    def get_report(self) -> Dict[str, Any]:
        """
        Get inspection report with errors and warnings.

        :return: Dictionary containing inspection results
        """
        return {
            "template_path": str(self.template_path),
            "errors": self.errors,
            "warnings": self.warnings,
            "is_valid": len(self.errors) == 0,
        }


def inspect_fastapi_template(template_path: str) -> Dict[str, Any]:
    """
    Convenience function to inspect a FastAPI template.

    :param template_path: Path to the template to inspect
    :return: Inspection report dictionary
    """
    with TemplateInspector(template_path) as inspector:
        is_valid = inspector.inspect_template()
        report = inspector.get_report()

        if is_valid:
            print_success(f"Template {template_path} is valid!")
        else:
            print_error(f"Template {template_path} validation failed")
            for error in inspector.errors:
                print_error(f"  - {error}")

        if inspector.warnings:
            for warning in inspector.warnings:
                print_warning(f"  - {warning}")

    return report


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print_error("Usage: python inspector.py <template_dir>")
        sys.exit(1)

    template_dir = sys.argv[1]
    inspect_fastapi_template(template_dir)
