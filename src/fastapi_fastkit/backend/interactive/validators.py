# --------------------------------------------------------------------------
# Input validation utilities for interactive mode
#
# Provides validation functions for:
# - Package names
# - Project names
# - Feature compatibility checking
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import re
from typing import Any, Dict, List, Optional, Tuple

from fastapi_fastkit.utils.main import REGEX as EMAIL_REGEX


def validate_package_name(package: str) -> bool:
    """
    Validate package name format.

    Checks if the package name follows basic PyPI package naming conventions.
    Does not validate existence on PyPI (that will be added in v1.2.1+).

    Args:
        package: Package name to validate

    Returns:
        True if format is valid, False otherwise
    """
    if not package or not isinstance(package, str):
        return False

    # Remove version specifiers and extras for validation
    package_name = re.split(r"[<>=!\[]", package)[0].strip()

    # Basic package name pattern: letters, numbers, hyphens, underscores, dots
    # Must start with letter or number
    pattern = r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$"

    return bool(re.match(pattern, package_name))


def validate_project_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate project name.

    Args:
        name: Project name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Project name cannot be empty"

    if not name.replace("_", "").replace("-", "").isalnum():
        return (
            False,
            "Project name must contain only letters, numbers, hyphens, and underscores",
        )

    if name[0].isdigit():
        return False, "Project name cannot start with a number"

    # Check for Python keywords
    import keyword

    if keyword.iskeyword(name):
        return False, f"Project name '{name}' is a Python keyword"

    return True, None


def validate_email_format(email: str) -> bool:
    """
    Validate email address format using utils/main.py REGEX pattern.

    Args:
        email: Email address to validate

    Returns:
        True if format is valid, False otherwise
    """
    if not email:
        return False

    return bool(re.match(EMAIL_REGEX, email))


def validate_feature_compatibility(
    config: Dict[str, Any],
) -> Tuple[bool, Optional[str]]:
    """
    Check compatibility between selected features.

    Validates that selected features don't have conflicting requirements.

    Args:
        config: Project configuration dictionary

    Returns:
        Tuple of (is_compatible, warning_message)
    """
    warnings = []

    # Check if FastAPI-Users is selected with database
    if config.get("authentication") == "FastAPI-Users":
        db_type = config.get("database", {}).get("type", "None")
        if db_type == "None":
            warnings.append(
                "FastAPI-Users requires a database. Consider selecting PostgreSQL or MySQL."
            )

    # Check if Celery is selected with Redis
    if config.get("async_tasks") == "Celery" or config.get("async_tasks") == "Dramatiq":
        # These already include Redis in their dependencies
        pass

    # Check if caching Redis is selected along with task queue Redis
    cache_type = config.get("caching", "None")
    task_type = config.get("async_tasks", "None")
    if cache_type == "Redis" and task_type in ["Celery", "Dramatiq"]:
        # This is actually compatible, just a note
        warnings.append(
            "Info: Redis will be used for both caching and task queue (shared dependency)."
        )

    # If there are warnings, return them
    if warnings:
        return True, " | ".join(warnings)

    return True, None


def sanitize_custom_packages(packages: List[str]) -> List[str]:
    """
    Clean and deduplicate custom package list.

    Args:
        packages: List of package names (possibly with duplicates or empty strings)

    Returns:
        Cleaned list of unique package names
    """
    if not packages:
        return []

    # Remove empty strings and strip whitespace
    cleaned = [pkg.strip() for pkg in packages if pkg and pkg.strip()]

    # Remove duplicates while preserving order
    seen = set()
    unique_packages = []
    for pkg in cleaned:
        pkg_lower = pkg.lower()
        if pkg_lower not in seen:
            seen.add(pkg_lower)
            unique_packages.append(pkg)

    # Validate each package name
    valid_packages = [pkg for pkg in unique_packages if validate_package_name(pkg)]

    return valid_packages
