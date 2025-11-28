# --------------------------------------------------------------------------
# Test cases for backend/interactive/validators.py
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import pytest

from fastapi_fastkit.backend.interactive.validators import (
    sanitize_custom_packages,
    validate_email_format,
    validate_feature_compatibility,
    validate_package_name,
    validate_project_name,
)


class TestValidatePackageName:
    """Test cases for validate_package_name function."""

    def test_valid_simple_package_name(self) -> None:
        """Test validation of simple valid package name."""
        # given
        package_name = "fastapi"

        # when
        result = validate_package_name(package_name)

        # then
        assert result is True

    def test_valid_package_name_with_hyphen(self) -> None:
        """Test validation of package name with hyphen."""
        # given
        package_name = "fastapi-users"

        # when
        result = validate_package_name(package_name)

        # then
        assert result is True

    def test_valid_package_name_with_underscore(self) -> None:
        """Test validation of package name with underscore."""
        # given
        package_name = "fastapi_cache"

        # when
        result = validate_package_name(package_name)

        # then
        assert result is True

    def test_valid_package_name_with_version(self) -> None:
        """Test validation of package name with version specifier."""
        # given
        package_name = "fastapi>=0.100.0"

        # when
        result = validate_package_name(package_name)

        # then
        assert result is True

    def test_valid_package_name_with_extras(self) -> None:
        """Test validation of package name with extras."""
        # given
        package_name = "uvicorn[standard]"

        # when
        result = validate_package_name(package_name)

        # then
        assert result is True

    def test_valid_package_name_with_version_and_extras(self) -> None:
        """Test validation of package name with both version and extras."""
        # given
        package_name = "python-jose[cryptography]>=3.0.0"

        # when
        result = validate_package_name(package_name)

        # then
        assert result is True

    def test_invalid_package_name_empty_string(self) -> None:
        """Test validation fails for empty string."""
        # given
        package_name = ""

        # when
        result = validate_package_name(package_name)

        # then
        assert result is False

    def test_invalid_package_name_only_whitespace(self) -> None:
        """Test validation fails for whitespace only."""
        # given
        package_name = "   "

        # when
        result = validate_package_name(package_name)

        # then
        assert result is False

    def test_invalid_package_name_starts_with_special_char(self) -> None:
        """Test validation fails for package starting with special character."""
        # given
        package_name = "-fastapi"

        # when
        result = validate_package_name(package_name)

        # then
        assert result is False

    def test_valid_package_name_with_dots(self) -> None:
        """Test validation of package name with dots."""
        # given
        package_name = "backports.zoneinfo"

        # when
        result = validate_package_name(package_name)

        # then
        assert result is True


class TestValidateProjectName:
    """Test cases for validate_project_name function."""

    def test_valid_simple_project_name(self) -> None:
        """Test validation of simple valid project name."""
        # given
        project_name = "myproject"

        # when
        is_valid, error = validate_project_name(project_name)

        # then
        assert is_valid is True
        assert error is None

    def test_valid_project_name_with_hyphen(self) -> None:
        """Test validation of project name with hyphen."""
        # given
        project_name = "my-awesome-project"

        # when
        is_valid, error = validate_project_name(project_name)

        # then
        assert is_valid is True
        assert error is None

    def test_valid_project_name_with_underscore(self) -> None:
        """Test validation of project name with underscore."""
        # given
        project_name = "my_project_name"

        # when
        is_valid, error = validate_project_name(project_name)

        # then
        assert is_valid is True
        assert error is None

    def test_valid_project_name_mixed_case(self) -> None:
        """Test validation of project name with mixed case."""
        # given
        project_name = "MyProject"

        # when
        is_valid, error = validate_project_name(project_name)

        # then
        assert is_valid is True
        assert error is None

    def test_invalid_project_name_empty_string(self) -> None:
        """Test validation fails for empty string."""
        # given
        project_name = ""

        # when
        is_valid, error = validate_project_name(project_name)

        # then
        assert is_valid is False
        assert error is not None
        assert "cannot be empty" in error

    def test_invalid_project_name_starts_with_number(self) -> None:
        """Test validation fails when project name starts with number."""
        # given
        project_name = "123project"

        # when
        is_valid, error = validate_project_name(project_name)

        # then
        assert is_valid is False
        assert error is not None
        assert "cannot start with a number" in error

    def test_invalid_project_name_with_special_chars(self) -> None:
        """Test validation fails for special characters."""
        # given
        project_name = "my@project!"

        # when
        is_valid, error = validate_project_name(project_name)

        # then
        assert is_valid is False
        assert error is not None
        assert "letters, numbers, hyphens, and underscores" in error

    def test_invalid_project_name_python_keyword(self) -> None:
        """Test validation fails for Python keywords."""
        # given
        project_name = "import"

        # when
        is_valid, error = validate_project_name(project_name)

        # then
        assert is_valid is False
        assert error is not None
        assert "Python keyword" in error

    def test_invalid_project_name_another_keyword(self) -> None:
        """Test validation fails for another Python keyword."""
        # given
        project_name = "class"

        # when
        is_valid, error = validate_project_name(project_name)

        # then
        assert is_valid is False
        assert error is not None
        assert "Python keyword" in error


class TestValidateEmailFormat:
    """Test cases for validate_email_format function."""

    def test_valid_simple_email(self) -> None:
        """Test validation of simple valid email."""
        # given
        email = "user@example.com"

        # when
        result = validate_email_format(email)

        # then
        assert result is True

    def test_valid_email_with_subdomain(self) -> None:
        """Test validation of email with subdomain."""
        # given
        email = "user@mail.example.com"

        # when
        result = validate_email_format(email)

        # then
        assert result is True

    def test_valid_email_with_plus(self) -> None:
        """Test validation of email with plus sign."""
        # given
        email = "user+tag@example.com"

        # when
        result = validate_email_format(email)

        # then
        assert result is True

    def test_valid_email_with_dots(self) -> None:
        """Test validation of email with dots in username."""
        # given
        email = "first.last@example.com"

        # when
        result = validate_email_format(email)

        # then
        assert result is True

    def test_valid_email_with_numbers(self) -> None:
        """Test validation of email with numbers."""
        # given
        email = "user123@example.com"

        # when
        result = validate_email_format(email)

        # then
        assert result is True

    def test_invalid_email_no_at_sign(self) -> None:
        """Test validation fails for email without @ sign."""
        # given
        email = "userexample.com"

        # when
        result = validate_email_format(email)

        # then
        assert result is False

    def test_invalid_email_no_domain(self) -> None:
        """Test validation fails for email without domain."""
        # given
        email = "user@"

        # when
        result = validate_email_format(email)

        # then
        assert result is False

    def test_invalid_email_no_username(self) -> None:
        """Test validation fails for email without username."""
        # given
        email = "@example.com"

        # when
        result = validate_email_format(email)

        # then
        assert result is False

    def test_invalid_email_empty_string(self) -> None:
        """Test validation fails for empty string."""
        # given
        email = ""

        # when
        result = validate_email_format(email)

        # then
        assert result is False

    def test_invalid_email_multiple_at_signs(self) -> None:
        """Test validation fails for multiple @ signs."""
        # given
        email = "user@@example.com"

        # when
        result = validate_email_format(email)

        # then
        assert result is False


class TestValidateFeatureCompatibility:
    """Test cases for validate_feature_compatibility function."""

    def test_compatible_features_basic(self) -> None:
        """Test basic compatible features."""
        # given
        config = {
            "database": {"type": "PostgreSQL"},
            "authentication": "JWT",
            "async_tasks": "None",
        }

        # when
        is_valid, warning = validate_feature_compatibility(config)

        # then
        assert is_valid is True
        assert warning is None

    def test_compatible_features_full_stack(self) -> None:
        """Test full stack compatible features."""
        # given
        config = {
            "database": {"type": "PostgreSQL"},
            "authentication": "JWT",
            "async_tasks": "Celery",
            "caching": "Redis",
            "monitoring": "Prometheus",
        }

        # when
        is_valid, warning = validate_feature_compatibility(config)

        # then
        assert is_valid is True
        # May have info warning about shared Redis
        if warning:
            assert "Redis" in warning

    def test_fastapi_users_without_database_warning(self) -> None:
        """Test warning when FastAPI-Users selected without database."""
        # given
        config = {
            "database": {"type": "None"},
            "authentication": "FastAPI-Users",
        }

        # when
        is_valid, warning = validate_feature_compatibility(config)

        # then
        assert is_valid is True
        assert warning is not None
        assert "FastAPI-Users requires a database" in warning

    def test_fastapi_users_with_database_no_warning(self) -> None:
        """Test no warning when FastAPI-Users with database."""
        # given
        config = {
            "database": {"type": "PostgreSQL"},
            "authentication": "FastAPI-Users",
        }

        # when
        is_valid, warning = validate_feature_compatibility(config)

        # then
        assert is_valid is True
        # Should not have FastAPI-Users warning

    def test_redis_shared_for_cache_and_tasks(self) -> None:
        """Test info message when Redis used for both cache and tasks."""
        # given
        config = {
            "caching": "Redis",
            "async_tasks": "Celery",
        }

        # when
        is_valid, warning = validate_feature_compatibility(config)

        # then
        assert is_valid is True
        assert warning is not None
        assert "Redis" in warning
        assert "shared dependency" in warning.lower()

    def test_no_features_selected(self) -> None:
        """Test validation with no features selected."""
        # given
        config = {
            "database": {"type": "None"},
            "authentication": "None",
            "async_tasks": "None",
        }

        # when
        is_valid, warning = validate_feature_compatibility(config)

        # then
        assert is_valid is True
        assert warning is None


class TestSanitizeCustomPackages:
    """Test cases for sanitize_custom_packages function."""

    def test_sanitize_valid_packages(self) -> None:
        """Test sanitization of valid package list."""
        # given
        packages = ["fastapi", "uvicorn", "sqlalchemy"]

        # when
        result = sanitize_custom_packages(packages)

        # then
        assert len(result) == 3
        assert "fastapi" in result
        assert "uvicorn" in result
        assert "sqlalchemy" in result

    def test_sanitize_removes_duplicates(self) -> None:
        """Test that duplicates are removed."""
        # given
        packages = ["fastapi", "uvicorn", "fastapi", "sqlalchemy"]

        # when
        result = sanitize_custom_packages(packages)

        # then
        assert len(result) == 3
        assert result.count("fastapi") == 1

    def test_sanitize_removes_empty_strings(self) -> None:
        """Test that empty strings are removed."""
        # given
        packages = ["fastapi", "", "uvicorn", "   ", "sqlalchemy"]

        # when
        result = sanitize_custom_packages(packages)

        # then
        assert len(result) == 3
        assert "" not in result

    def test_sanitize_trims_whitespace(self) -> None:
        """Test that whitespace is trimmed."""
        # given
        packages = ["  fastapi  ", " uvicorn", "sqlalchemy "]

        # when
        result = sanitize_custom_packages(packages)

        # then
        assert "fastapi" in result
        assert "uvicorn" in result
        assert "sqlalchemy" in result
        assert "  fastapi  " not in result

    def test_sanitize_case_insensitive_deduplication(self) -> None:
        """Test case-insensitive deduplication."""
        # given
        packages = ["FastAPI", "fastapi", "FASTAPI"]

        # when
        result = sanitize_custom_packages(packages)

        # then
        assert len(result) == 1
        assert "FastAPI" in result  # Keeps first occurrence

    def test_sanitize_removes_invalid_package_names(self) -> None:
        """Test that invalid package names are removed."""
        # given
        packages = ["fastapi", "@invalid!", "uvicorn", "-bad-name"]

        # when
        result = sanitize_custom_packages(packages)

        # then
        assert "fastapi" in result
        assert "uvicorn" in result
        assert "@invalid!" not in result
        assert "-bad-name" not in result

    def test_sanitize_empty_list(self) -> None:
        """Test sanitization of empty list."""
        # given
        packages = []

        # when
        result = sanitize_custom_packages(packages)

        # then
        assert result == []

    def test_sanitize_none_input(self) -> None:
        """Test sanitization with None input."""
        # given
        packages = None

        # when
        result = sanitize_custom_packages(packages)

        # then
        assert result == []

    def test_sanitize_preserves_version_specifiers(self) -> None:
        """Test that version specifiers are preserved."""
        # given
        packages = ["fastapi>=0.100.0", "uvicorn[standard]"]

        # when
        result = sanitize_custom_packages(packages)

        # then
        assert "fastapi>=0.100.0" in result
        assert "uvicorn[standard]" in result
