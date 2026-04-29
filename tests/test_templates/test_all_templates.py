# --------------------------------------------------------------------------
# Dynamic template testing for all FastAPI templates
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from pathlib import Path
from typing import Any, Dict, Generator, List

import pytest
from click.testing import CliRunner

from fastapi_fastkit.cli import fastkit_cli
from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.utils.main import is_fastkit_project


class TemplateTestConfig:
    """Template test configuration and discovery"""

    @classmethod
    def discover_templates(cls) -> List[str]:
        """Dynamically discover all available templates"""
        settings = FastkitConfig()
        template_dir = Path(settings.FASTKIT_TEMPLATE_ROOT)

        # Exclude non-template directories
        excluded_dirs = {"__pycache__", "modules"}

        templates = [
            d.name
            for d in template_dir.iterdir()
            if d.is_dir() and d.name not in excluded_dirs
        ]

        return sorted(templates)  # Sort for consistent test order

    @classmethod
    def get_template_metadata(cls, template_name: str) -> Dict[str, Any]:
        """Get template-specific test metadata"""
        # You can customize test parameters per template here
        metadata = {
            "expected_files": ["setup.py", "README.md", "src/main.py"],
            "required_dirs": ["src", "tests"],
            "package_manager": "uv",  # Default package manager
        }

        # Template-specific customizations
        template_configs = {
            "fastapi-dockerized": {
                "expected_files": list(metadata["expected_files"]) + ["Dockerfile"],
            },
            "fastapi-psql-orm": {
                "expected_files": list(metadata["expected_files"]) + ["alembic.ini"],
                "required_dirs": list(metadata["required_dirs"]) + ["src/alembic"],
            },
            "fastapi-mcp": {
                "expected_files": list(metadata["expected_files"]),
            },
            # Pyproject-first domain-oriented starter — no setup.py, the
            # FastAPI app entry point lives under src/app/, and domains are
            # grouped under src/app/domains/.
            "fastapi-domain-starter": {
                "expected_files": [
                    "README.md",
                    "pyproject.toml",
                    "src/app/main.py",
                    "src/app/core/config.py",
                    "src/app/api/health.py",
                    "src/app/domains/items/router.py",
                ],
                "required_dirs": [
                    "src",
                    "tests",
                    "src/app",
                    "src/app/core",
                    "src/app/db",
                    "src/app/api",
                    "src/app/domains",
                    "src/app/domains/items",
                ],
            },
        }

        if template_name in template_configs:
            metadata.update(template_configs[template_name])

        return metadata


class TestAllTemplates:
    """Unified test class for all FastAPI templates"""

    runner: CliRunner = CliRunner()

    @pytest.fixture
    def temp_dir(self, tmpdir: Any) -> Generator[str, None, None]:
        """Temporary directory fixture"""
        original_cwd = os.getcwd()
        os.chdir(str(tmpdir))
        yield str(tmpdir)
        os.chdir(original_cwd)

    @pytest.mark.parametrize("template_name", TemplateTestConfig.discover_templates())
    def test_template_creation(self, template_name: str, temp_dir: str) -> None:
        """Test template creation for all discovered templates"""
        # Given
        project_name = f"test-{template_name}"
        author = "test-author"
        author_email = "test@example.com"
        description = f"A test FastAPI project with {template_name} template"

        metadata = TemplateTestConfig.get_template_metadata(template_name)

        # When
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", template_name],
            input="\n".join(
                [
                    project_name,
                    author,
                    author_email,
                    description,
                    metadata["package_manager"],
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )

        # Then
        project_path = Path(temp_dir) / project_name

        # Basic assertions
        assert (
            project_path.exists()
        ), f"Project directory was not created for {template_name}"
        assert (
            result.exit_code == 0
        ), f"CLI command failed for {template_name}: {result.output}"
        assert (
            "Success" in result.output
        ), f"Success message not found for {template_name}"

        # Template identification
        assert is_fastkit_project(
            str(project_path)
        ), f"Not identified as fastkit project: {template_name}"

        # Check expected files
        for expected_file in metadata["expected_files"]:
            file_path = project_path / expected_file
            assert (
                file_path.exists()
            ), f"Expected file missing in {template_name}: {expected_file}"

        # Check required directories
        for required_dir in metadata["required_dirs"]:
            dir_path = project_path / required_dir
            assert (
                dir_path.exists()
            ), f"Required directory missing in {template_name}: {required_dir}"

    @pytest.mark.parametrize("template_name", TemplateTestConfig.discover_templates())
    def test_template_metadata_injection(
        self, template_name: str, temp_dir: str
    ) -> None:
        """Test that project metadata is properly injected for all templates"""
        # Given
        project_name = f"metadata-test-{template_name}"
        author = "Metadata Author"
        author_email = "metadata@example.com"
        description = f"Metadata test for {template_name}"

        metadata = TemplateTestConfig.get_template_metadata(template_name)

        # When
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", template_name],
            input="\n".join(
                [
                    project_name,
                    author,
                    author_email,
                    description,
                    metadata["package_manager"],
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )

        # Then
        project_path = Path(temp_dir) / project_name
        assert result.exit_code == 0

        # Check setup.py contains injected metadata
        setup_py = project_path / "setup.py"
        if setup_py.exists():
            setup_content = setup_py.read_text()
            assert (
                project_name in setup_content
            ), f"Project name not found in setup.py for {template_name}"
            assert (
                author in setup_content
            ), f"Author not found in setup.py for {template_name}"
            assert (
                author_email in setup_content
            ), f"Author email not found in setup.py for {template_name}"

    def test_template_discovery(self) -> None:
        """Test that template discovery works correctly"""
        templates = TemplateTestConfig.discover_templates()

        # Should have discovered templates
        assert len(templates) > 0, "No templates discovered"

        # Should not include excluded directories
        excluded = {"__pycache__", "modules"}
        for template in templates:
            assert (
                template not in excluded
            ), f"Excluded directory found in templates: {template}"

        # Should be sorted
        assert templates == sorted(
            templates
        ), "Templates should be sorted for consistent test order"

    @pytest.mark.parametrize("package_manager", ["pip", "uv", "pdm", "poetry"])
    def test_fastapi_domain_starter_supports_all_package_managers(
        self, package_manager: str, temp_dir: str
    ) -> None:
        """Regression: domain-starter must succeed under every supported manager.

        The pyproject-first template still needs to work when a user picks
        ``pip``, ``pdm``, or ``poetry`` from the CLI prompt — otherwise the
        recommended modern default would be silently broken on three of the
        four supported package managers.
        """
        # Given
        project_name = f"manager-test-{package_manager}"
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-domain-starter"],
            input="\n".join(
                [
                    project_name,
                    "test-author",
                    "test@example.com",
                    "Domain starter package-manager check",
                    package_manager,
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )

        # Then
        project_path = Path(temp_dir) / project_name
        assert result.exit_code == 0, (
            f"startdemo failed for fastapi-domain-starter with "
            f"{package_manager}: {result.output}"
        )
        assert (
            project_path.exists()
        ), f"Project directory missing for {package_manager} run"
        assert is_fastkit_project(str(project_path))
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "src" / "app" / "main.py").exists()

    @pytest.mark.parametrize("template_name", TemplateTestConfig.discover_templates())
    def test_template_structure_validation(self, template_name: str) -> None:
        """Test that template directories have required structure"""
        settings = FastkitConfig()
        template_path = Path(settings.FASTKIT_TEMPLATE_ROOT) / template_name

        # Template directory should exist
        assert template_path.exists(), f"Template directory not found: {template_name}"
        assert (
            template_path.is_dir()
        ), f"Template path is not directory: {template_name}"

        # Should have README.md-tpl
        readme_path = template_path / "README.md-tpl"
        assert readme_path.exists(), f"README.md-tpl not found in {template_name}"

        # Should have at least one metadata file (pyproject.toml-tpl preferred,
        # setup.py-tpl accepted for backward compatibility).
        pyproject_path = template_path / "pyproject.toml-tpl"
        setup_path = template_path / "setup.py-tpl"
        assert (
            pyproject_path.exists() or setup_path.exists()
        ), f"Neither pyproject.toml-tpl nor setup.py-tpl found in {template_name}"
