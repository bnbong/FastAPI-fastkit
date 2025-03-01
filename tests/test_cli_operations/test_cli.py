# NOTE: For panel outputs, assertions may not work properly due to ANSI output issues even when output strings are identical.
# --------------------------------------------------------------------------
# Testcases of base CLI operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import subprocess
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

    def test_startdemo(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join(
                ["test-project", "bnbong", "bbbong9@gmail.com", "test project", "Y"]
            ),
        )

        # then
        project_path = Path(temp_dir) / "test-project"
        assert project_path.exists() and project_path.is_dir()
        assert "Success" in result.output

        # Check core module files
        expected_files = {
            "main": ["src/main.py", "main.py"],
            "setup": ["setup.py", "src/setup.py"],
            "config": {
                "files": ["settings.py", "config.py"],
                "paths": ["src/core", "src", ""],
            },
        }

        found_files = {"main": False, "setup": False, "config": False}

        # Check main.py
        for main_path in expected_files["main"]:
            file_path = project_path / main_path
            if file_path.exists() and file_path.is_file():
                found_files["main"] = True
                break

        # Check setup.py
        for setup_path in expected_files["setup"]:
            file_path = project_path / setup_path
            if file_path.exists() and file_path.is_file():
                found_files["setup"] = True
                with open(file_path, "r") as f:
                    content = f.read()
                    assert "test-project" in content
                    assert "bnbong" in content
                    assert "bbbong9@gmail.com" in content
                break

        # Check config files
        for config_path in expected_files["config"]["paths"]:  # type: ignore
            for config_file in expected_files["config"]["files"]:  # type: ignore
                file_path = project_path / config_path / config_file
                if file_path.exists() and file_path.is_file():
                    found_files["config"] = True
                    break
            if found_files["config"]:
                break

        assert all(found_files.values()), "Not all core module files were found"

    def test_delete_demoproject(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-project"
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
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

    def test_init_minimal(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-minimal"
        author = "test-author"
        author_email = "test@example.com"
        description = "A minimal FastAPI project"

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init"],
            input="\n".join(
                [project_name, author, author_email, description, "minimal", "Y"]
            ),
        )

        # then
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()
        assert "Success" in result.output

        setup_py = project_path / "setup.py"
        if setup_py.exists():
            with open(setup_py, "r") as f:
                content = f.read()
                assert project_name in content
                assert author in content
                assert author_email in content
                assert description in content

        with open(project_path / "requirements.txt", "r") as f:
            content = f.read()
            assert "fastapi" in content
            assert "uvicorn" in content
            assert "sqlalchemy" not in content

        venv_path = project_path / ".venv"
        assert venv_path.exists() and venv_path.is_dir()

        pip_list = subprocess.run(
            [str(venv_path / "bin" / "pip"), "list"], capture_output=True, text=True
        )
        installed_packages = pip_list.stdout.lower()
        assert "fastapi" in installed_packages
        assert "uvicorn" in installed_packages

    def test_init_full(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-full"
        author = "test-author"
        author_email = "test@example.com"
        description = "A full FastAPI project"

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init"],
            input="\n".join(
                [project_name, author, author_email, description, "full", "Y"]
            ),
        )

        # then
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()
        assert "Success" in result.output

        setup_py = project_path / "setup.py"
        if setup_py.exists():
            with open(setup_py, "r") as f:
                content = f.read()
                assert project_name in content
                assert author in content
                assert author_email in content
                assert description in content

        expected_deps = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "alembic",
            "pytest",
            "redis",
            "celery",
        ]

        with open(project_path / "requirements.txt", "r") as f:
            content = f.read()
            for dep in expected_deps:
                assert dep in content

        venv_path = project_path / ".venv"
        assert venv_path.exists() and venv_path.is_dir()

        pip_list = subprocess.run(
            [str(venv_path / "bin" / "pip"), "list"], capture_output=True, text=True
        )
        installed_packages = pip_list.stdout.lower()

        for dep in expected_deps:
            assert dep in installed_packages

    def test_init_existing_project(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-existing"
        os.makedirs(os.path.join(temp_dir, project_name))

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init"],
            input="\n".join(
                [
                    project_name,
                    "test-author",
                    "test@example.com",
                    "test description",
                    "minimal",
                ]
            ),
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
            ["startdemo", "fastapi-default"],
            input="\n".join(
                [project_name, "bnbong", "bbbong9@gmail.com", "test project", "Y"]
            ),
        )

        project_path = Path(temp_dir) / project_name
        assert project_path.exists()

        # when/then
        from fastapi_fastkit.utils.main import is_fastkit_project

        assert is_fastkit_project(str(project_path)) is True

        # Create a non-fastkit project
        non_fastkit_path = Path(temp_dir) / "non-fastkit"
        os.makedirs(non_fastkit_path)
        with open(non_fastkit_path / "setup.py", "w") as f:
            f.write("# Regular project setup")

        assert is_fastkit_project(str(non_fastkit_path)) is False
