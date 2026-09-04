# --------------------------------------------------------------------------
# Regression tests for the destructive / corrupting failure modes found in
# the independent safety review of the generation pipeline.
#
# Each test names the behaviour it pins down rather than the review item, but
# they all share one theme: generating a project must never destroy or corrupt
# something the user already had.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import ast
import os
import tomllib
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from fastapi_fastkit.backend.main import (
    _ensure_pyproject_fastkit_markers,
    escape_placeholder_value,
    insert_import_line,
    insert_statement_line,
)
from fastapi_fastkit.backend.scaffolder import (
    ProjectScaffolder,
    ScaffoldOptions,
    cleanup_failed_project,
)
from fastapi_fastkit.core.settings import FastkitConfig

HOSTILE_NAME = 'my"proj'
HOSTILE_AUTHOR = "A\\B"
HOSTILE_DESCRIPTION = 'He said "hi"'


def _settings(workspace: str) -> FastkitConfig:
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
        "assume_yes": True,
    }
    base.update(overrides)
    return ScaffoldOptions(**base)


class TestRollbackSafety:
    """Rollback must only ever remove a directory this run created."""

    @pytest.fixture(autouse=True)
    def _workspace(self, tmp_path: Path) -> None:
        self.workspace = str(tmp_path)
        self.settings = _settings(self.workspace)

    def test_cleanup_keeps_a_directory_that_existed_before_the_run(
        self, tmp_path: Path
    ) -> None:
        # given
        project_dir = tmp_path / "existing"
        project_dir.mkdir()
        notes = project_dir / "NOTES.txt"
        notes.write_text("years of notes")

        # when
        cleanup_failed_project(
            str(project_dir),
            str(tmp_path),
            create_project_folder=True,
            project_dir_pre_existed=True,
        )

        # then
        assert notes.read_text() == "years of notes"

    def test_cleanup_still_removes_a_directory_this_run_created(
        self, tmp_path: Path
    ) -> None:
        # given
        project_dir = tmp_path / "fresh"
        project_dir.mkdir()
        (project_dir / "main.py").write_text("app = 1")

        # when
        cleanup_failed_project(
            str(project_dir),
            str(tmp_path),
            create_project_folder=True,
            project_dir_pre_existed=False,
        )

        # then
        assert not project_dir.exists()

    def test_failed_run_into_an_existing_directory_keeps_the_users_files(self) -> None:
        # given: the target directory is already there with the user's own file
        project_dir = Path(self.workspace) / "scaffold-test"
        project_dir.mkdir()
        notes = project_dir / "NOTES.txt"
        notes.write_text("years of notes")
        scaffolder = ProjectScaffolder(self.settings, _options())

        # when
        with patch(
            "fastapi_fastkit.backend.scaffolder.inject_project_metadata",
            side_effect=RuntimeError("simulated metadata failure"),
        ):
            with pytest.raises(RuntimeError):
                scaffolder.run()

        # then
        assert notes.read_text() == "years of notes"


class TestInPlaceDeploymentScope:
    """Deploying in place must not rewrite unrelated workspace files."""

    @pytest.fixture(autouse=True)
    def _workspace(self, tmp_path: Path) -> None:
        self.workspace = str(tmp_path)
        self.settings = _settings(self.workspace)

    def test_unrelated_workspace_files_are_left_alone(self) -> None:
        # given: a file the user already had, carrying a placeholder token
        bystander = Path(self.workspace) / "my_notes.md"
        original = "TODO for <project_name> by <author>\n"
        bystander.write_text(original)
        scaffolder = ProjectScaffolder(
            self.settings, _options(create_project_folder=False)
        )

        # when
        scaffolder.run()

        # then
        assert bystander.read_text() == original

    def test_existing_targets_lists_the_files_a_run_would_overwrite(self) -> None:
        # given
        clash = Path(self.workspace) / "README.md"
        clash.write_text("mine")
        scaffolder = ProjectScaffolder(
            self.settings, _options(create_project_folder=False)
        )

        # when
        clashes = scaffolder.existing_targets()

        # then
        assert "README.md" in clashes

    def test_declining_the_overwrite_prompt_writes_nothing(self) -> None:
        # given
        clash = Path(self.workspace) / "README.md"
        clash.write_text("mine")
        scaffolder = ProjectScaffolder(
            self.settings, _options(create_project_folder=False, assume_yes=False)
        )

        # when
        with (
            patch(
                "fastapi_fastkit.backend.scaffolder.sys.stdin.isatty", return_value=True
            ),
            patch(
                "fastapi_fastkit.backend.scaffolder.click.confirm", return_value=False
            ),
        ):
            with pytest.raises(Exception, match="aborted"):
                scaffolder.run()

        # then
        assert clash.read_text() == "mine"


class TestMetadataEscaping:
    """Quotes and backslashes in metadata must not break generated files."""

    @pytest.fixture(autouse=True)
    def _workspace(self, tmp_path: Path) -> None:
        self.workspace = str(tmp_path)
        self.settings = _settings(self.workspace)

    def test_escape_is_chosen_per_file_type(self) -> None:
        # given / when / then
        assert escape_placeholder_value('a"b', "x.toml") == 'a\\"b'
        assert escape_placeholder_value("A\\B", "x.toml") == "A\\\\B"
        assert escape_placeholder_value('a"b', "x.py") == 'a\\"b'
        assert escape_placeholder_value("A\\B", "x.py") == "A\\\\B"
        assert escape_placeholder_value('a"b', "x.md") == 'a"b'

    def test_generated_project_still_parses_with_hostile_metadata(self) -> None:
        # given
        scaffolder = ProjectScaffolder(
            self.settings,
            _options(
                project_name="hostile-proj",
                author=HOSTILE_AUTHOR,
                description=HOSTILE_DESCRIPTION,
            ),
        )

        # when
        result = scaffolder.run()

        # then
        pyproject = Path(result.project_dir) / "pyproject.toml"
        parsed = tomllib.loads(pyproject.read_text())
        assert HOSTILE_DESCRIPTION in parsed["project"]["description"]

        for py_file in Path(result.project_dir).rglob("*.py"):
            ast.parse(py_file.read_text(), filename=str(py_file))

    def test_hostile_project_name_survives_config_and_pyproject(
        self, tmp_path: Path
    ) -> None:
        # given: the name is normally rejected by validation, but the escaping
        # layer must hold on its own for callers that bypass the CLI
        from fastapi_fastkit.backend.main import inject_project_metadata

        project_dir = tmp_path / "proj"
        (project_dir / "src").mkdir(parents=True)
        pyproject = project_dir / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "<project_name>"\n'
            'description = "<description>"\n'
            'authors = [{ name = "<author>", email = "<author_email>" }]\n'
        )
        config = project_dir / "src" / "config.py"
        config.write_text('PROJECT_NAME: str = "<project_name>"\n')

        # when
        inject_project_metadata(
            str(project_dir),
            HOSTILE_NAME,
            HOSTILE_AUTHOR,
            "bbbong9@gmail.com",
            HOSTILE_DESCRIPTION,
            files=[str(pyproject), str(config)],
        )

        # then
        parsed = tomllib.loads(pyproject.read_text())
        assert parsed["project"]["name"] == HOSTILE_NAME
        assert parsed["project"]["authors"][0]["name"] == HOSTILE_AUTHOR
        module = ast.parse(config.read_text())
        assigned = module.body[0]
        assert isinstance(assigned, ast.AnnAssign)
        assert isinstance(assigned.value, ast.Constant)
        assert assigned.value.value == HOSTILE_NAME


class TestFastkitSectionRewrite:
    """Re-stamping the metadata table must not shred the existing one."""

    def test_rewriting_a_block_with_a_features_array(self) -> None:
        # given
        content = (
            "[project]\n"
            'name = "demo"\n'
            'description = "demo project"\n'
            "\n"
            "[tool.fastapi-fastkit]\n"
            "managed = true\n"
            'features = ["database:PostgreSQL", "authentication:JWT"]\n'
            'app_module = "src.main:app"\n'
            "\n"
            "[tool.black]\n"
            "line-length = 88\n"
        )

        # when
        updated = _ensure_pyproject_fastkit_markers(
            content,
            {
                "template": "fastapi-default",
                "app_module": "C:\\tmp",
                "features": ["caching:Redis"],
            },
        )

        # then
        parsed = tomllib.loads(updated)
        section = parsed["tool"]["fastapi-fastkit"]
        assert section["features"] == ["caching:Redis"]
        assert section["app_module"] == "C:\\tmp"
        assert parsed["tool"]["black"]["line-length"] == 88
        assert updated.count("[tool.fastapi-fastkit]") == 1

    def test_rewriting_a_trailing_block_at_end_of_file(self) -> None:
        # given
        content = (
            "[project]\n"
            'name = "demo"\n'
            "\n"
            "[tool.fastapi-fastkit]\n"
            "managed = true\n"
            'features = ["a:b"]\n'
        )

        # when
        updated = _ensure_pyproject_fastkit_markers(content, {"template": "t"})

        # then
        parsed = tomllib.loads(updated)
        assert parsed["tool"]["fastapi-fastkit"]["template"] == "t"
        assert "features" not in parsed["tool"]["fastapi-fastkit"]


class TestAnchorInsertion:
    """Only real comment anchors count, and imports keep a valid prelude."""

    def test_anchor_inside_a_string_literal_is_ignored(self) -> None:
        # given
        content = 'ANCHOR_DOC = "# fastkit:routes"\n'

        # when
        updated = insert_statement_line(content, "app.include_router(router)")

        # then
        assert updated.splitlines()[0] == 'ANCHOR_DOC = "# fastkit:routes"'
        assert updated.splitlines()[1] == "app.include_router(router)"

    def test_docstring_mentioning_the_anchor_is_ignored(self) -> None:
        # given
        content = '"""Templates may write # fastkit:imports here."""\n\napp = 1\n'

        # when
        updated = insert_import_line(content, "import os")

        # then
        assert updated.splitlines()[1] == "import os"

    def test_first_of_several_anchors_wins(self) -> None:
        # given
        content = "# fastkit:routes\nx = 1\n# fastkit:routes\n"

        # when
        updated = insert_statement_line(content, "app.include_router(router)")

        # then
        lines = updated.splitlines()
        assert lines[1] == "app.include_router(router)"
        assert lines.count("app.include_router(router)") == 1

    def test_import_goes_below_the_future_import(self) -> None:
        # given
        content = '"""Doc."""\n\nfrom __future__ import annotations\n\napp = 1\n'

        # when
        updated = insert_import_line(content, "import os")

        # then
        lines = updated.splitlines()
        assert lines.index("from __future__ import annotations") < lines.index(
            "import os"
        )

    def test_import_goes_below_the_module_docstring(self) -> None:
        # given
        content = '"""Doc."""\n\napp = 1\n'

        # when
        updated = insert_import_line(content, "import os")

        # then
        assert updated.startswith('"""Doc."""\n')
        assert ast.parse(updated)
        module = ast.parse(updated)
        assert ast.get_docstring(module) == "Doc."
