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
from fastapi_fastkit.utils.main import is_fastkit_project, read_fastkit_metadata

#: Tokens a template declares for the generator to fill in.
PLACEHOLDER_TOKENS = ("<project_name>", "<author>", "<author_email>", "<description>")

#: File suffixes worth scanning for placeholder residue. "" covers extensionless
#: files such as Dockerfile and .env, which templates do use placeholders in.
_TEXT_SUFFIXES = {"", ".py", ".toml", ".md", ".txt", ".yml", ".yaml", ".ini", ".sh"}


def _files_with_placeholder_residue(project_path: Path) -> List[str]:
    """Return project-relative paths of files still carrying a placeholder."""
    residue: List[str] = []
    for path in project_path.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        if any(part in {".venv", "venv", "__pycache__"} for part in path.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if any(token in content for token in PLACEHOLDER_TOKENS):
            residue.append(str(path.relative_to(project_path)))
    return residue


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
        # Every template is pyproject-first: ``pyproject.toml`` is the single
        # metadata file, and ``setup.py-tpl`` no longer ships with any of them.
        metadata = {
            "expected_files": ["pyproject.toml", "README.md", "src/main.py"],
            "required_dirs": ["src", "tests"],
            "package_manager": "uv",  # Default package manager
        }

        # Layout shared by the modern ``src/app/`` templates: the FastAPI app
        # lives under ``src/app/main.py`` with routers grouped per domain.
        app_layout_files = [
            "README.md",
            "pyproject.toml",
            "src/app/main.py",
            "src/app/core/config.py",
            "src/app/api/health.py",
        ]
        app_layout_dirs = [
            "src",
            "tests",
            "src/app",
            "src/app/core",
            "src/app/api",
        ]

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
            # Pyproject-first domain-oriented starter — the FastAPI app entry
            # point lives under src/app/, and domains are grouped under
            # src/app/domains/.
            "fastapi-domain-starter": {
                "expected_files": app_layout_files
                + ["src/app/domains/items/router.py"],
                "required_dirs": app_layout_dirs
                + ["src/app/db", "src/app/domains", "src/app/domains/items"],
            },
            # JWT authentication starter: auth + users domains on top of the
            # same src/app layout, with Alembic migrations for the schema.
            "fastapi-auth-jwt": {
                "expected_files": app_layout_files
                + [
                    "alembic.ini",
                    "src/app/core/security.py",
                    "src/app/domains/auth/router.py",
                    "src/app/domains/users/router.py",
                ],
                "required_dirs": app_layout_dirs
                + [
                    "src/app/db",
                    "src/app/alembic",
                    "src/app/domains",
                    "src/app/domains/auth",
                    "src/app/domains/users",
                ],
            },
            # SQLModel starter: shared CRUD helpers plus an items domain.
            "fastapi-sqlmodel": {
                "expected_files": app_layout_files
                + [
                    "alembic.ini",
                    "src/app/crud/base.py",
                    "src/app/domains/items/router.py",
                ],
                "required_dirs": app_layout_dirs
                + [
                    "src/app/db",
                    "src/app/crud",
                    "src/app/alembic",
                    "src/app/domains",
                    "src/app/domains/items",
                ],
            },
            # LLM agent starter: chat endpoint backed by an llm/ package and a
            # pluggable conversation memory.
            "fastapi-llm-agent": {
                "expected_files": app_layout_files
                + [
                    "src/app/api/chat.py",
                    "src/app/llm/agent.py",
                    "src/app/memory/base.py",
                    "src/app/schemas/chat.py",
                ],
                "required_dirs": app_layout_dirs
                + ["src/app/llm", "src/app/memory", "src/app/schemas"],
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

        # pyproject.toml is the metadata file every template ships.
        pyproject = project_path / "pyproject.toml"
        assert pyproject.exists(), f"pyproject.toml missing for {template_name}"
        pyproject_content = pyproject.read_text()
        assert (
            project_name in pyproject_content
        ), f"Project name not found in pyproject.toml for {template_name}"
        assert (
            author in pyproject_content
        ), f"Author not found in pyproject.toml for {template_name}"
        assert (
            author_email in pyproject_content
        ), f"Author email not found in pyproject.toml for {template_name}"

        # Placeholders must not survive anywhere in the generated project —
        # README.md, .env and tests/conftest.py use them too, not just the
        # metadata files.
        residue = _files_with_placeholder_residue(project_path)
        assert (
            not residue
        ), f"Unsubstituted placeholders in {template_name}: " + ", ".join(
            sorted(residue)
        )

        # template-config.yml drives the template inspector and must never be
        # copied into a user's project.
        assert not (project_path / "template-config.yml").exists(), (
            f"template-config.yml leaked into generated project for " f"{template_name}"
        )

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

        Run with ``--no-venv``: what is under test is the generation pipeline
        (template copy, metadata injection, dependency file for the chosen
        manager), not whether ``pdm``/``poetry`` happen to be installed on the
        machine running the suite.
        """
        # Given
        project_name = f"manager-test-{package_manager}"
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-domain-starter", "--no-venv"],
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
            "Success" in result.output
        ), f"No success message for {package_manager}: {result.output}"
        assert (
            project_path.exists()
        ), f"Project directory missing for {package_manager} run"
        assert is_fastkit_project(str(project_path))
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "src" / "app" / "main.py").exists()
        assert (project_path / "src" / "app" / "api" / "health.py").exists()
        assert (project_path / "tests").is_dir()

        # The recorded package manager must match what the user picked, so
        # later fastkit commands drive the right tool.
        metadata = read_fastkit_metadata(str(project_path))
        assert metadata.get("package_manager") == package_manager
        assert metadata.get("app_module") == "src.app.main:app"

        assert not _files_with_placeholder_residue(project_path)

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

        # Templates are pyproject-first: pyproject.toml-tpl is the metadata
        # file, and no template may reintroduce a setup.py-tpl shim.
        pyproject_path = template_path / "pyproject.toml-tpl"
        assert (
            pyproject_path.exists()
        ), f"pyproject.toml-tpl not found in {template_name}"
        assert not (template_path / "setup.py-tpl").exists(), (
            f"{template_name} ships a setup.py-tpl; declare metadata in "
            f"pyproject.toml-tpl instead"
        )
