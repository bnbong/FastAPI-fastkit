# NOTE: For panel outputs, assertions may not work properly due to ANSI output issues even when output strings are identical.
# --------------------------------------------------------------------------
# Testcases of base CLI operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from pathlib import Path
from typing import Any

from click.testing import CliRunner

from fastapi_fastkit.cli import fastkit_cli


class TestCLI:
    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()

    def teardown_method(self, console: Any) -> None:
        os.chdir(self.current_workspace)

    def test_echo(self) -> None:
        # given

        # when
        result = self.runner.invoke(fastkit_cli, ["echo"])

        # then
        assert "About FastAPI-fastkit" in result.output
        assert "⚡️ FastAPI fastkit - fastest FastAPI initializer. ⚡️" in result.output
        assert "Deploy FastAPI app foundation instantly at your local!" in result.output
        assert "Project Maintainer : bnbong(JunHyeok Lee)" in result.output
        assert "Github : https://github.com/bnbong/FastAPI-fastkit" in result.output

    def test_startup(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startup", "fastapi-default"],
            input="\n".join(
                ["test-project", "bnbong", "bbbong9@gmail.com", "test project", "Y"]
            ),
        )

        # then
        project_path = Path(temp_dir) / "test-project"
        assert project_path.exists() and project_path.is_dir()
        assert "Success" in result.output

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

    def test_deleteproject(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-project"
        result = self.runner.invoke(
            fastkit_cli,
            ["startup", "fastapi-default"],
            input="\n".join(
                [project_name, "bnbong", "bbbong9@gmail.com", "test project", "Y"]
            ),
        )
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()
        assert "Success" in result.output

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["deleteproject", project_name],
            input="Y",
        )

        # then
        assert "Success" in result.output
        assert not project_path.exists()

    def test_list_templates(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(fastkit_cli, ["list-templates"])

        # then
        assert "Available Templates" in result.output
        assert "fastapi-default" in result.output
        assert "fastapi-dockerized" in result.output

    def test_startproject_minimal(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-minimal"

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startproject"],
            input="\n".join([project_name, "minimal"]),
        )

        # then
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()
        assert (
            f"✨ Project '{project_name}' has been created successfully!"
            in result.output
        )

        requirements_path = project_path / "requirements.txt"
        assert requirements_path.exists() and requirements_path.is_file()

        with open(requirements_path, "r") as f:
            content = f.read()
            assert "fastapi" in content
            assert "uvicorn" in content
            assert "sqlalchemy" not in content

        venv_path = project_path / "venv"
        assert venv_path.exists() and venv_path.is_dir()

    def test_startproject_full(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-full"

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startproject"],
            input="\n".join([project_name, "full"]),
        )

        # then
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()
        assert (
            f"Project '{project_name}' has been created successfully!" in result.output
        )

        requirements_path = project_path / "requirements.txt"
        assert requirements_path.exists() and requirements_path.is_file()

        with open(requirements_path, "r") as f:
            content = f.read()
            assert "fastapi" in content
            assert "uvicorn" in content
            assert "sqlalchemy" in content
            assert "redis" in content
            assert "celery" in content

        venv_path = project_path / "venv"
        assert venv_path.exists() and venv_path.is_dir()

    def test_startproject_existing_project(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-existing"
        os.makedirs(os.path.join(temp_dir, project_name))

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startproject"],
            input="\n".join([project_name, "minimal"]),
        )

        # then
        assert "❌" in result.output
        assert f"Error: Project '{project_name}' already exists" in result.output

    def test_is_fastkit_project(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-project"

        # Create a regular project
        result = self.runner.invoke(
            fastkit_cli,
            ["startup", "fastapi-default"],
            input="\n".join(
                [project_name, "bnbong", "bbbong9@gmail.com", "test project", "Y"]
            ),
        )

        project_path = Path(temp_dir) / project_name
        assert project_path.exists()

        # when/then
        from fastapi_fastkit.cli import is_fastkit_project

        assert is_fastkit_project(str(project_path)) is True

        # Create a non-fastkit project
        non_fastkit_path = Path(temp_dir) / "non-fastkit"
        os.makedirs(non_fastkit_path)
        with open(non_fastkit_path / "setup.py", "w") as f:
            f.write("# Regular project setup")

        assert is_fastkit_project(str(non_fastkit_path)) is False
