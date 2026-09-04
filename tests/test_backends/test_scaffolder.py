# --------------------------------------------------------------------------
# Testcases of the ProjectScaffolder service.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from fastapi_fastkit.backend.scaffolder import (
    ProjectScaffolder,
    ScaffoldOptions,
    cleanup_failed_project,
)
from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.utils.main import read_fastkit_metadata


def _settings(workspace: str) -> FastkitConfig:
    """Build a settings object rooted at a throwaway workspace."""
    settings = FastkitConfig()
    settings.USER_WORKSPACE = workspace
    return settings


def _options(**overrides: Any) -> ScaffoldOptions:
    base: Dict[str, Any] = {
        "project_name": "scaffold-test",
        "author": "bnbong",
        "author_email": "bbbong9@gmail.com",
        "description": "scaffolder testcase project",
        "package_manager": "pip",
        "template": "fastapi-default",
        "with_venv": False,
        "with_install": False,
    }
    base.update(overrides)
    return ScaffoldOptions(**base)


class TestProjectScaffolder:
    @pytest.fixture(autouse=True)
    def _workspace(self, tmp_path: Path) -> None:
        self.workspace = str(tmp_path)
        self.settings = _settings(self.workspace)

    def test_build_metadata_records_the_generation_contract(self) -> None:
        # given
        config = {
            "database": {"type": "PostgreSQL"},
            "authentication": "JWT",
            "utilities": ["CORS"],
        }
        options = _options(
            template="fastapi-domain-starter",
            preset_id="domain-starter",
            config=config,
        )

        # when
        metadata = ProjectScaffolder(self.settings, options).build_metadata()

        # then
        assert metadata["managed"] is True
        assert metadata["template"] == "fastapi-domain-starter"
        assert metadata["preset"] == "domain-starter"
        assert metadata["package_manager"] == "pip"
        assert metadata["app_module"] == "src.app.main:app"
        assert "database:PostgreSQL" in metadata["features"]
        assert "authentication:JWT" in metadata["features"]
        assert "utilities:CORS" in metadata["features"]

    def test_app_module_follows_the_template_layout(self) -> None:
        # given / when
        classic = ProjectScaffolder(self.settings, _options(template="fastapi-default"))
        domain = ProjectScaffolder(
            self.settings, _options(template="fastapi-domain-starter")
        )

        # then
        assert classic.app_module == "src.main:app"
        assert domain.app_module == "src.app.main:app"

    def test_run_writes_metadata_into_pyproject(self) -> None:
        # given
        scaffolder = ProjectScaffolder(self.settings, _options())

        # when
        result = scaffolder.run()

        # then
        assert os.path.isdir(result.project_dir)
        metadata = read_fastkit_metadata(result.project_dir)
        assert metadata["managed"] is True
        assert metadata["template"] == "fastapi-default"
        assert metadata["app_module"] == "src.main:app"
        assert metadata["package_manager"] == "pip"
        assert "version" in metadata

    def test_run_skips_venv_and_install_when_disabled(self) -> None:
        # given
        scaffolder = ProjectScaffolder(self.settings, _options())

        # when
        with (
            patch(
                "fastapi_fastkit.backend.scaffolder.create_venv_with_manager"
            ) as mock_venv,
            patch(
                "fastapi_fastkit.backend.scaffolder.install_dependencies_with_manager"
            ) as mock_install,
        ):
            result = scaffolder.run()

        # then
        mock_venv.assert_not_called()
        mock_install.assert_not_called()
        assert result.venv_path == ""

    def test_run_creates_venv_but_skips_install(self) -> None:
        # given
        scaffolder = ProjectScaffolder(
            self.settings, _options(with_venv=True, with_install=False)
        )

        # when
        with (
            patch(
                "fastapi_fastkit.backend.scaffolder.create_venv_with_manager",
                return_value="/tmp/fake-venv",
            ) as mock_venv,
            patch(
                "fastapi_fastkit.backend.scaffolder.install_dependencies_with_manager"
            ) as mock_install,
        ):
            result = scaffolder.run()

        # then
        mock_venv.assert_called_once()
        mock_install.assert_not_called()
        assert result.venv_path == "/tmp/fake-venv"

    def test_run_rolls_back_the_project_folder_on_failure(self) -> None:
        # given
        scaffolder = ProjectScaffolder(self.settings, _options())

        # when
        with patch(
            "fastapi_fastkit.backend.scaffolder.inject_project_metadata",
            side_effect=RuntimeError("simulated metadata failure"),
        ):
            with pytest.raises(RuntimeError, match="simulated metadata failure"):
                scaffolder.run()

        # then
        assert not os.path.exists(os.path.join(self.workspace, "scaffold-test"))

    def test_run_never_deletes_the_workspace_on_failure(self) -> None:
        # given: deploying in place means project_dir == workspace
        bystander = Path(self.workspace) / "unrelated.txt"
        bystander.write_text("keep me")
        scaffolder = ProjectScaffolder(
            self.settings, _options(create_project_folder=False)
        )

        # when
        with patch(
            "fastapi_fastkit.backend.scaffolder.inject_project_metadata",
            side_effect=RuntimeError("simulated metadata failure"),
        ):
            with pytest.raises(RuntimeError):
                scaffolder.run()

        # then
        assert os.path.isdir(self.workspace)
        assert bystander.read_text() == "keep me"

    def test_preview_writes_nothing(self) -> None:
        # given
        scaffolder = ProjectScaffolder(self.settings, _options(dry_run=True))

        # when
        result = scaffolder.run()

        # then
        assert result.dry_run is True
        assert not os.path.exists(os.path.join(self.workspace, "scaffold-test"))
        assert os.listdir(self.workspace) == []
        assert result.dependencies  # template stack was resolved for the report

    def test_missing_template_is_reported_before_anything_is_written(self) -> None:
        # given
        scaffolder = ProjectScaffolder(
            self.settings, _options(template="does-not-exist")
        )

        # when & then
        with pytest.raises(Exception, match="does not exist"):
            scaffolder.run()
        assert os.listdir(self.workspace) == []


class TestCleanupFailedProject:
    def test_removes_created_project_folder(self, tmp_path: Path) -> None:
        # given
        workspace = tmp_path / "workspace"
        project = workspace / "proj"
        project.mkdir(parents=True)

        # when
        cleanup_failed_project(str(project), str(workspace), True)

        # then
        assert not project.exists()

    def test_keeps_workspace_when_deployed_in_place(self, tmp_path: Path) -> None:
        # given
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # when
        cleanup_failed_project(str(workspace), str(workspace), True)

        # then
        assert workspace.exists()

    def test_noop_when_folder_was_not_created(self, tmp_path: Path) -> None:
        # given
        project = tmp_path / "proj"
        project.mkdir()

        # when
        cleanup_failed_project(str(project), str(tmp_path), False)

        # then
        assert project.exists()
