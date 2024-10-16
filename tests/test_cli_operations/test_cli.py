# --------------------------------------------------------------------------
# Testcases of base CLI operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os

from click.testing import CliRunner
from pathlib import Path

from fastapi_fastkit.cli import fastkit_cli


class TestCLI:
    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()

    def teardown_method(self, console) -> None:
        os.chdir(self.current_workspace)

    def test_echo(self) -> None:
        # given

        # when
        result = self.runner.invoke(fastkit_cli, ["echo"])  # type: ignore

        # then
        assert (
            "╭─────────────────────────── About FastAPI-fastkit ────────────────────────────╮"
            in result.output
        )
        assert (
            "│     ⚡️ FastAPI fastkit - fastest FastAPI initializer. ⚡️"
            in result.output
        )
        assert (
            "│     Deploy FastAPI app foundation instantly at your local!"
            in result.output
        )
        assert "│     - Project Maintainer : bnbong(JunHyeok Lee)" in result.output
        assert (
            "│     - Github : https://github.com/bnbong/FastAPI-fastkit"
            in result.output
        )

    def test_startproject(self, temp_dir) -> None:
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(
            fastkit_cli,  # type: ignore
            ["startproject", "fastapi-default"],
            input="\n".join(
                ["test-project", "bnbong", "bbbong9@gmail.com", "test project", "Y"]
            ),
        )

        # then
        project_path = (
            Path(temp_dir) / "test-project"
        )  # TODO : change this after adding folder naming feature.
        assert project_path.exists() and project_path.is_dir()
        assert (
            f"FastAPI project 'test-project' from 'fastapi-default' has been created and saved to {temp_dir}!"
            in result.output
        )

        expected_files = ["main.py", "setup.py"]
        for file in expected_files:
            file_path = project_path / file
            assert file_path.exists() and file_path.is_file()

        main_py_path = project_path / "main.py"
        setup_py_path = project_path / "setup.py"

        with open(main_py_path, "r") as main_py:
            main_py_content = main_py.read()
            assert "test-project" in main_py_content
            assert "test project" in main_py_content

        with open(setup_py_path, "r") as setup_py:
            setup_py_content = setup_py.read()
            assert "test-project" in setup_py_content
            assert "bnbong" in setup_py_content
            assert "bbbong9@gmail.com" in setup_py_content
