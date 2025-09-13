#!/usr/bin/env python3
# --------------------------------------------------------------------------
# Inspect only changed FastAPI templates (for pre-commit / local use)
# --------------------------------------------------------------------------
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Set

# Ensure src is importable
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from fastapi_fastkit.backend.inspector import inspect_fastapi_template

TEMPLATE_DIR = PROJECT_ROOT / "src" / "fastapi_fastkit" / "fastapi_project_template"


def get_changed_files() -> List[str]:
    """Return a list of changed files according to git (staged + unstaged)."""
    # Include staged and unstaged changes compared to HEAD
    cmd = [
        "git",
        "diff",
        "--name-only",
        "--cached",
    ]
    staged = subprocess.run(cmd, capture_output=True, text=True, check=False)
    cmd_unstaged = [
        "git",
        "diff",
        "--name-only",
    ]
    unstaged = subprocess.run(cmd_unstaged, capture_output=True, text=True, check=False)

    files: Set[str] = set()
    if staged.stdout:
        files.update(
            [line.strip() for line in staged.stdout.splitlines() if line.strip()]
        )
    if unstaged.stdout:
        files.update(
            [line.strip() for line in unstaged.stdout.splitlines() if line.strip()]
        )
    return sorted(files)


def extract_changed_templates(changed_files: List[str]) -> List[str]:
    """Map changed files to template directory names under TEMPLATE_DIR."""
    templates: Set[str] = set()
    template_root_str = str(TEMPLATE_DIR).rstrip("/")

    for f in changed_files:
        fp = (PROJECT_ROOT / f).resolve()
        # Only consider files under template root
        try:
            if str(fp).startswith(template_root_str):
                # template name is immediate child dir of TEMPLATE_DIR
                # e.g., .../fastapi_project_template/<template>/...
                rel = str(fp)[len(template_root_str) + 1 :]
                parts = rel.split(os.sep)
                if parts:
                    templates.add(parts[0])
        except Exception:
            continue

    # Filter only directories that truly exist
    return sorted([t for t in templates if (TEMPLATE_DIR / t).is_dir()])


def main() -> int:
    changed_files = get_changed_files()
    changed_templates = extract_changed_templates(changed_files)

    if not changed_templates:
        print("No template changes detected; skipping inspection.")
        return 0

    print(f"Detected changed templates: {', '.join(changed_templates)}")
    any_failed = False

    for template in changed_templates:
        t_path = TEMPLATE_DIR / template
        print(f"Inspecting changed template: {template}\n  Path: {t_path}")
        try:
            result = inspect_fastapi_template(str(t_path))
            if not result.get("is_valid", False):
                any_failed = True
        except Exception as e:
            any_failed = True
            print(f"Exception while inspecting {template}: {e}")

    if any_failed:
        print("Template inspection failed for at least one changed template.")
        return 1

    print("All changed templates passed inspection.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
