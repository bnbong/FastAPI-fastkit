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
                    "Y",
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
                    "Y",
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

        # Should have setup.py-tpl
        setup_path = template_path / "setup.py-tpl"
        assert setup_path.exists(), f"setup.py-tpl not found in {template_name}"
