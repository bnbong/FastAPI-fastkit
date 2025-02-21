# --------------------------------------------------------------------------
# The Module inspect FastAPI template is appropriate
#
# This module will be read by Github Action when contributor
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
from typing import Any, Dict, List

from fastapi_fastkit.backend.main import (
    create_venv,
    find_template_core_modules,
    install_dependencies,
)
from fastapi_fastkit.backend.transducer import copy_and_convert_template
from fastapi_fastkit.utils.main import print_error, print_success, print_warning


class TemplateInspector:
    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.temp_dir = os.path.join(os.path.dirname(__file__), "temp")

        # Create temp directory and copy template
        os.makedirs(self.temp_dir, exist_ok=True)
        copy_and_convert_template(str(self.template_path), self.temp_dir)

    def __del__(self) -> None:
        """Cleanup temp directory when inspector is destroyed."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def inspect_template(self) -> bool:
        """Inspect the template is valid FastAPI application."""
        checks = [
            self._check_file_structure,
            self._check_file_extensions,
            self._check_dependencies,
            self._check_fastapi_implementation,
            self._test_template,
        ]

        for check in checks:
            if not check():
                return False
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

        with open(req_path) as f:
            deps = f.read().splitlines()
            package_names = [dep.split("==")[0] for dep in deps if dep]
            if "fastapi" not in package_names:
                self.errors.append(
                    "FastAPI dependency not found in requirements.txt-tpl"
                )
                return False
        return True

    def _check_fastapi_implementation(self) -> bool:
        """Check if the template has a proper FastAPI server implementation."""
        core_modules = find_template_core_modules(self.temp_dir)

        if not core_modules["main"]:
            self.errors.append("main.py not found in template")
            return False

        with open(core_modules["main"]) as f:
            content = f.read()
            if "FastAPI" not in content or "app" not in content:
                self.errors.append("FastAPI app creation not found in main.py")
                return False
        return True

    def _test_template(self) -> bool:
        """Run the tests in the converted template directory."""
        test_dir = Path(self.temp_dir) / "tests"
        if not test_dir.exists():
            self.errors.append("Tests directory not found")
            return False

        try:
            # Create virtual environment
            venv_path = create_venv(self.temp_dir)

            # Install dependencies
            install_dependencies(self.temp_dir, venv_path)

            # Run tests using the venv's pytest
            if os.name == "nt":  # Windows
                pytest_path = os.path.join(venv_path, "Scripts", "pytest")
            else:  # Linux/Mac
                pytest_path = os.path.join(venv_path, "bin", "pytest")

            result = subprocess.run(
                [pytest_path, str(test_dir)],
                capture_output=True,
                text=True,
                cwd=self.temp_dir,
            )

            if result.returncode != 0:
                self.errors.append(f"Tests failed: {result.stderr}")
                return False

        except Exception as e:
            self.errors.append(f"Error running tests: {e}")
            return False

        return True


def inspect_template(template_path: str) -> Dict[str, Any]:
    """Run the template inspection and return the result."""
    inspector = TemplateInspector(template_path)
    is_valid = inspector.inspect_template()
    result: dict[str, Any] = {
        "valid": is_valid,
        "errors": inspector.errors,
        "warnings": inspector.warnings,
    }

    if result["valid"]:
        print_success("Template inspection passed successfully! ✨")
    elif result["errors"]:
        error_messages = [str(error) for error in result["errors"]]
        print_error(
            "Template inspection failed with following errors:\n"
            + "\n".join(f"- {error}" for error in error_messages)
        )

    if result["warnings"]:
        warning_messages = [str(warning) for warning in result["warnings"]]
        print_warning(
            "Template has following warnings:\n"
            + "\n".join(f"- {warning}" for warning in warning_messages)
        )

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python inspector.py <template_dir>")
        sys.exit(1)

    template_dir = sys.argv[1]
    inspect_template(template_dir)
