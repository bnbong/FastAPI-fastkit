import os
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from fastapi_fastkit.cli import fastkit_cli
from fastapi_fastkit.utils.main import is_fastkit_project


class TestFastAPIDefault:
    runner = CliRunner()

    @pytest.fixture
    def temp_dir(self, tmpdir):
        os.chdir(tmpdir)
        yield str(tmpdir)
        # Clean up
        os.chdir(os.path.expanduser("~"))

    def test_startdemo_fastapi_default(self, temp_dir):
        # given
        project_name = "test-default"
        author = "test-author"
        author_email = "test@example.com"
        description = "A test FastAPI project with default template"

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join([project_name, author, author_email, description, "Y"]),
        )

        # then
        project_path = Path(temp_dir) / project_name

        assert project_path.exists(), "Project directory was not created"
        assert result.exit_code == 0, f"CLI command failed: {result.output}"
        assert "Success" in result.output, "Success message not found in output"

        assert is_fastkit_project(
            str(project_path)
        ), "Not identified as a fastkit project"

        assert (project_path / "setup.py").exists(), "setup.py not found"
        assert (project_path / "src" / "main.py").exists(), "main.py not found"
        assert (
            project_path / "requirements.txt"
        ).exists(), "requirements.txt not found"
        assert (project_path / ".venv").exists(), "Virtual environment not created"

        with open(project_path / "setup.py", "r") as f:
            setup_content = f.read()
            assert project_name in setup_content, "Project name not injected"
            assert author in setup_content, "Author not injected"
            assert description in setup_content, "Description not injected"
