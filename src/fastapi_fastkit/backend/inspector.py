# --------------------------------------------------------------------------
# The Module inspect FastAPI template is appropriate
#
# This module will be read by Github Action when contributor
#   makes a PR of adding new FastAPI template.
#
# @author bnbong
# --------------------------------------------------------------------------
import subprocess
import sys
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
            package_names = [dep.split("==")[0] for dep in deps if dep]
            if "fastapi" not in package_names:
                self.errors.append("FastAPI dependency not found")
                return False
        return True

    def _check_fastapi_implementation(self) -> bool:
        """Check if the template has a proper FastAPI server implementation."""
        main_paths = [
            self.template_path / "src/main.py-tpl",
            self.template_path / "main.py-tpl",
        ]

        main_file_found = False
        for main_path in main_paths:
            if main_path.exists():
                main_file_found = True
                with open(main_path) as f:
                    content = f.read()
                    if "uvicorn.run" not in content:
                        self.errors.append(f"Web server call not found in {main_path}")
                        return False
                break

        if not main_file_found:
            self.errors.append("main.py-tpl not found in either src/ or root directory")
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python inspector.py <template_dir>")
        sys.exit(1)

    template_dir = sys.argv[1]
    result = inspect_template(template_dir)
    print(result)
