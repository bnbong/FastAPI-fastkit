#!/usr/bin/env python3
# --------------------------------------------------------------------------
# Local template inspection script for testing.
# This script mimics the GitHub Actions workflow for local development.
#
# Usage:
#   python scripts/inspect-templates.py
#   python scripts/inspect-templates.py --templates fastapi-default,fastapi-async-crud
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Add src to path to import fastapi_fastkit modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from fastapi_fastkit.backend.inspector import inspect_fastapi_template


def get_templates_to_inspect(specific_templates: str = "") -> List[str]:
    """Get list of templates to inspect."""
    template_dir = project_root / "src" / "fastapi_fastkit" / "fastapi_project_template"

    # Skip these directories
    skip_dirs = {"modules", "__pycache__"}

    all_templates = [
        d.name
        for d in template_dir.iterdir()
        if d.is_dir() and d.name not in skip_dirs and not d.name.startswith(".")
    ]

    if specific_templates:
        requested = [t.strip() for t in specific_templates.split(",")]
        return [t for t in requested if t in all_templates]

    return sorted(all_templates)


def inspect_template(template_name: str) -> Dict[str, Any]:
    """Inspect a single template."""
    template_path = (
        project_root
        / "src"
        / "fastapi_fastkit"
        / "fastapi_project_template"
        / template_name
    )

    print(f"🔍 Inspecting template: {template_name}")
    print(f"   Path: {template_path}")

    try:
        result = inspect_fastapi_template(str(template_path))
        result["template_name"] = template_name
        result["inspection_time"] = datetime.now(timezone.utc).isoformat()

        if result.get("is_valid", False):
            print(f"✅ {template_name}: PASSED")
        else:
            print(f"❌ {template_name}: FAILED")
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"   ERROR: {error}")
            if result.get("warnings"):
                for warning in result["warnings"]:
                    print(f"   WARNING: {warning}")

        return result

    except Exception as e:
        error_result = {
            "template_name": template_name,
            "is_valid": False,
            "errors": [f"Inspection failed with exception: {str(e)}"],
            "warnings": [],
            "inspection_time": datetime.now(timezone.utc).isoformat(),
        }
        print(f"💥 {template_name}: EXCEPTION - {str(e)}")
        return error_result


def main() -> None:
    """Main inspection function."""
    parser = argparse.ArgumentParser(description="Inspect FastAPI templates locally")
    parser.add_argument(
        "--templates",
        type=str,
        default="",
        help="Specific templates to inspect (comma-separated, leave empty for all)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="template_inspection_results.json",
        help="Output JSON file for results",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Change to project root directory
    os.chdir(project_root)

    # Get templates to inspect
    templates = get_templates_to_inspect(args.templates)

    if not templates:
        print("❌ No templates found to inspect!")
        sys.exit(1)

    print(f"📋 Found {len(templates)} templates to inspect: {', '.join(templates)}")
    if args.verbose:
        print(f"🔧 Working directory: {os.getcwd()}")
        print(f"📁 Template directory: src/fastapi_fastkit/fastapi_project_template/")
    print("=" * 60)

    # Inspect each template
    results = []
    failed_templates = []

    for template in templates:
        result = inspect_template(template)
        results.append(result)

        if not result.get("is_valid", False):
            failed_templates.append(template)

        print("-" * 40)

    # Save results
    output_data = {
        "inspection_date": datetime.now(timezone.utc).isoformat(),
        "total_templates": len(templates),
        "passed_templates": len(templates) - len(failed_templates),
        "failed_templates": len(failed_templates),
        "results": results,
    }

    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)

    # Summary
    print("=" * 60)
    print("📊 INSPECTION SUMMARY")
    print(f"   Total templates: {len(templates)}")
    print(f"   ✅ Passed: {len(templates) - len(failed_templates)}")
    print(f"   ❌ Failed: {len(failed_templates)}")

    if failed_templates:
        print(f"   Failed templates: {', '.join(failed_templates)}")
        print(f"📄 Detailed results saved to: {args.output}")
        sys.exit(1)
    else:
        print("🎉 All templates passed inspection!")
        print(f"📄 Results saved to: {args.output}")


if __name__ == "__main__":
    main()
