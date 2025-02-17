# --------------------------------------------------------------------------
# The Module inspect FastAPI template is appropriate
#
# This module will be read by Github Action when contributor
#   makes a PR of adding new FastAPI template.
#
# @author bnbong
# --------------------------------------------------------------------------
import subprocess
from pathlib import Path
from typing import Any, Dict, List


class TemplateInspector:
    def __init__(self, template_path: str):
        self.template_path = Path(template_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []

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
            "src/main.py-tpl",
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
        """Check the dependencies."""
        req_path = self.template_path / "requirements.txt-tpl"
        if not req_path.exists():
            self.errors.append("requirements.txt-tpl not found")
            return False

        with open(req_path) as f:
            deps = f.read().splitlines()
            if "fastapi" not in deps:
                self.errors.append("FastAPI dependency not found")
                return False
        return True

    def _check_fastapi_implementation(self) -> bool:
        """Check the FastAPI implementation."""
        main_path = self.template_path / "src/main.py-tpl"
        if not main_path.exists():
            self.errors.append("main.py-tpl not found")
            return False

        with open(main_path) as f:
            content = f.read()
            if "from fastapi import FastAPI" not in content:
                self.errors.append("FastAPI import not found in main.py-tpl")
                return False
        return True

    def _test_template(self) -> bool:
        """Run the tests."""
        test_dir = self.template_path / "tests"
        if not test_dir.exists():
            self.errors.append("Tests directory not found")
            return False

        try:
            result = subprocess.run(
                ["pytest", str(test_dir)], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.errors.append(f"Tests failed: {result.stderr}")
                return False
        except Exception as e:
            self.errors.append(f"Error running tests: {e}")
            return False
        return True


def inspect_template(template_path: str) -> Dict[str, Any | List[str]]:
    """Run the template inspection and return the result."""
    inspector = TemplateInspector(template_path)
    is_valid = inspector.inspect_template()

    return {
        "valid": is_valid,
        "errors": inspector.errors,
        "warnings": inspector.warnings,
    }
