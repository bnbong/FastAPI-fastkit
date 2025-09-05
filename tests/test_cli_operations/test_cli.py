# NOTE: For panel outputs, assertions may not work properly due to ANSI output issues even when output strings are identical.
# --------------------------------------------------------------------------
# Testcases of base CLI operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

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
                [
                    "test-project",
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
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

    def test_startdemo_invalid_template(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "invalid-template"],
            input="\n".join(
                [
                    "test-project",
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )

        # then
        assert result.exit_code != 0
        assert "Error" in result.output or "Invalid" in result.output

    def test_startdemo_cancel_confirmation(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join(
                [
                    "test-project",
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "N",
                ]
            ),
        )

        # then
        # CLI returns 0 even when user cancels (just prints error and returns)
        assert result.exit_code == 0
        assert "Project creation aborted!" in result.output

    def test_startdemo_backend_error(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)

        # Test with invalid template to simulate backend error
        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "non-existent-template"],
            input="\n".join(
                [
                    "test-startdemo-error",
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )

        # then
        # CLI should handle error gracefully
        assert (
            result.exit_code != 0
            or "Error" in result.output
            or "does not exist" in result.output
        )

    def test_delete_demoproject(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-project"
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join(
                [
                    project_name,
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
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

    def test_delete_demoproject_cancel(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-project"
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join(
                [
                    project_name,
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["deleteproject", project_name],
            input="N",
        )

        # then
        assert project_path.exists()  # Should still exist

    def test_delete_demoproject_nonexistent(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "nonexistent-project"

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["deleteproject", project_name],
            input="Y",
        )

        # then
        # CLI returns 0 even when project doesn't exist (just prints error and returns)
        assert result.exit_code == 0
        assert "does not exist" in result.output

    def test_list_templates(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(fastkit_cli, ["list-templates"])

        # then
        assert "Available Templates" in result.output
        assert "fastapi-default" in result.output
        assert "fastapi-dockerized" in result.output

    @patch("fastapi_fastkit.backend.package_managers.uv_manager.UvManager.is_available")
    @patch("subprocess.run")
    def test_init_minimal(
        self, mock_subprocess: MagicMock, mock_uv_available: MagicMock, temp_dir: str
    ) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-minimal"
        author = "test-author"
        author_email = "test@example.com"
        description = "A minimal FastAPI project"

        # Mock package manager as available and subprocess calls
        mock_uv_available.return_value = True
        mock_subprocess.return_value.returncode = 0

        # Mock subprocess to create venv directory when called
        def mock_subprocess_side_effect(*args: Any, **kwargs: Any) -> MagicMock:
            if "venv" in str(args[0]):
                venv_path = Path(temp_dir) / project_name / ".venv"
                venv_path.mkdir(parents=True, exist_ok=True)
                # Also create Scripts/bin directory for pip path checks
                if os.name == "nt":
                    (venv_path / "Scripts").mkdir(exist_ok=True)
                else:
                    (venv_path / "bin").mkdir(exist_ok=True)
            mock_result = MagicMock()
            mock_result.returncode = 0
            return mock_result

        mock_subprocess.side_effect = mock_subprocess_side_effect

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init"],
            input="\n".join(
                [
                    project_name,
                    author,
                    author_email,
                    description,
                    "minimal",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
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

        # Check dependency file (pyproject.toml for uv)
        if (project_path / "pyproject.toml").exists():
            with open(project_path / "pyproject.toml", "r") as f:
                content = f.read()
                assert "fastapi" in content
                assert "uvicorn" in content
                assert "sqlalchemy" not in content
        else:
            with open(project_path / "requirements.txt", "r") as f:
                content = f.read()
                assert "fastapi" in content
                assert "uvicorn" in content
                assert "sqlalchemy" not in content

        venv_path = project_path / ".venv"
        assert venv_path.exists() and venv_path.is_dir()

        # Note: Actual dependency installation is mocked in tests
        # Check that subprocess.run was called for dependency installation
        assert (
            mock_subprocess.call_count >= 2
        )  # venv creation + dependency installation

    @patch("fastapi_fastkit.backend.package_managers.uv_manager.UvManager.is_available")
    @patch("subprocess.run")
    def test_init_full(
        self, mock_subprocess: MagicMock, mock_uv_available: MagicMock, temp_dir: str
    ) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-full"
        author = "test-author"
        author_email = "test@example.com"
        description = "A full FastAPI project"

        # Mock package manager as available and subprocess calls
        mock_uv_available.return_value = True
        mock_subprocess.return_value.returncode = 0

        # Mock subprocess to create venv directory when called
        def mock_subprocess_side_effect(*args: Any, **kwargs: Any) -> MagicMock:
            if "venv" in str(args[0]):
                venv_path = Path(temp_dir) / project_name / ".venv"
                venv_path.mkdir(parents=True, exist_ok=True)
                # Also create Scripts/bin directory for pip path checks
                if os.name == "nt":
                    (venv_path / "Scripts").mkdir(exist_ok=True)
                else:
                    (venv_path / "bin").mkdir(exist_ok=True)
            mock_result = MagicMock()
            mock_result.returncode = 0
            return mock_result

        mock_subprocess.side_effect = mock_subprocess_side_effect

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init"],
            input="\n".join(
                [
                    project_name,
                    author,
                    author_email,
                    description,
                    "full",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
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

        # Check dependency file (pyproject.toml for uv)
        if (project_path / "pyproject.toml").exists():
            with open(project_path / "pyproject.toml", "r") as f:
                content = f.read()
                assert "fastapi" in content
                assert "uvicorn" in content
                assert "sqlalchemy" in content
        else:
            with open(project_path / "requirements.txt", "r") as f:
                content = f.read()
                assert "fastapi" in content
                assert "uvicorn" in content
                assert "sqlalchemy" in content

        venv_path = project_path / ".venv"
        assert venv_path.exists() and venv_path.is_dir()

        # Note: Actual dependency installation is mocked in tests
        # Check that subprocess.run was called for dependency installation
        assert (
            mock_subprocess.call_count >= 2
        )  # venv creation + dependency installation

    def test_init_cancel_confirmation(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-cancel"

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init"],
            input="\n".join(
                [
                    project_name,
                    "author",
                    "email@example.com",
                    "description",
                    "minimal",
                    "N",
                ]
            ),
        )

        # then
        project_path = Path(temp_dir) / project_name
        assert not project_path.exists()

    def test_init_backend_error(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)

        # Test with existing project to simulate backend error scenario
        project_name = "test-backend-error"
        project_path = Path(temp_dir) / project_name
        project_path.mkdir()

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init"],
            input="\n".join(
                [
                    project_name,
                    "author",
                    "email@example.com",
                    "description",
                    "minimal",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )

        # then
        # CLI should handle existing project gracefully
        assert result.exit_code == 0
        assert "already exists" in result.output

    def test_init_existing_project(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-existing"
        project_path = Path(temp_dir) / project_name
        project_path.mkdir()

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init"],
            input="\n".join(
                [
                    project_name,
                    "author",
                    "email@example.com",
                    "description",
                    "minimal",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )

        # then
        # CLI returns 0 even when project already exists (just prints error and returns)
        assert result.exit_code == 0
        assert "already exists" in result.output

    def test_is_fastkit_project_function(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-project"
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join(
                [
                    project_name,
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()
        assert "Success" in result.output

        # when & then
        # Test the is_fastkit_project function directly since no CLI command exists
        from fastapi_fastkit.utils.main import is_fastkit_project

        assert is_fastkit_project(str(project_path)) is True

    def test_is_fastkit_project_function_not_fastkit(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_path = Path(temp_dir) / "regular-project"
        project_path.mkdir()

        # when & then
        # Test the is_fastkit_project function directly since no CLI command exists
        from fastapi_fastkit.utils.main import is_fastkit_project

        assert is_fastkit_project(str(project_path)) is False

    def test_runserver_command(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-project"
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join(
                [
                    project_name,
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()
        assert "Success" in result.output

        os.chdir(project_path)

        # when
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = self.runner.invoke(fastkit_cli, ["runserver"])

        # then
        assert result.exit_code == 0

    def test_runserver_no_venv_project(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_path = Path(temp_dir) / "regular-project2"
        project_path.mkdir()
        os.chdir(project_path)

        # when
        # Answer 'N' to "Do you want to continue with system Python?"
        result = self.runner.invoke(fastkit_cli, ["runserver"], input="N")

        # then
        # CLI returns 0 even when user declines to continue (just returns)
        assert result.exit_code == 0
        assert "Virtual environment not found" in result.output

    def test_addroute_command(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-project"
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join(
                [
                    project_name,
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()
        assert "Success" in result.output

        # when
        # addroute command requires route_name and project_dir as arguments
        result = self.runner.invoke(
            fastkit_cli, ["addroute", "test_route", project_name], input="Y"
        )

        # then
        assert result.exit_code == 0
        assert "Successfully added new route" in result.output

    def test_addroute_nonexistent_project(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "nonexistent-project"

        # when
        result = self.runner.invoke(
            fastkit_cli, ["addroute", "test_route", project_name], input="Y"
        )

        # then
        # CLI returns 0 even when project doesn't exist (just prints error and returns)
        assert result.exit_code == 0
        assert "does not exist" in result.output

    def test_addroute_cancel_confirmation(self, temp_dir: str) -> None:
        # given
        os.chdir(temp_dir)
        project_name = "test-project"
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join(
                [
                    project_name,
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()
        assert "Success" in result.output

        # when
        # addroute command requires route_name and project_dir as arguments
        result = self.runner.invoke(
            fastkit_cli, ["addroute", "test_route", project_name], input="N"
        )

        # then
        # CLI returns 0 even when user cancels (just prints error and returns)
        assert result.exit_code == 0
        assert "Operation cancelled!" in result.output

    def test_addroute_current_directory(self, temp_dir: str) -> None:
        """Test addroute command with current directory (.)"""
        # given
        os.chdir(temp_dir)
        project_name = "test-project"

        # First create a project
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join(
                [
                    project_name,
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "Y",  # Create new project folder
                ]
            ),
        )
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir()
        assert "Success" in result.output

        # Change to project directory
        os.chdir(project_path)

        # when
        # addroute command with current directory (.)
        result = self.runner.invoke(fastkit_cli, ["addroute", "user", "."], input="Y")

        # then
        assert result.exit_code == 0
        assert (
            "Successfully added new route 'user' to the current project!"
            in result.output
        )

    def test_addroute_current_directory_not_fastkit_project(
        self, temp_dir: str
    ) -> None:
        """Test addroute command with current directory when it's not a fastkit project"""
        # given
        os.chdir(temp_dir)

        # when
        # addroute command with current directory (.) but no fastkit project
        result = self.runner.invoke(fastkit_cli, ["addroute", "user", "."], input="Y")

        # then
        assert result.exit_code == 0
        assert "Current directory is not a FastAPI-fastkit project." in result.output

    def test_startdemo_no_project_folder(self, temp_dir: str) -> None:
        """Test startdemo with no project folder creation (deploy to current directory)."""
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "fastapi-default"],
            input="\n".join(
                [
                    "test-project-no-folder",
                    "bnbong",
                    "bbbong9@gmail.com",
                    "test project",
                    "uv",
                    "Y",  # Proceed with project creation
                    "N",  # Do not create new project folder
                ]
            ),
        )

        # then
        # Files should be deployed directly to temp_dir, not in a subfolder
        assert result.exit_code == 0
        assert "Success" in result.output

        # Check that main files exist directly in temp_dir
        main_py_paths = [Path(temp_dir) / "src" / "main.py", Path(temp_dir) / "main.py"]
        main_py_found = any(path.exists() for path in main_py_paths)
        assert main_py_found, "main.py should exist directly in current directory"

        # Ensure no project folder was created
        project_folder = Path(temp_dir) / "test-project-no-folder"
        assert (
            not project_folder.exists()
        ), "Project folder should not be created when user selects 'N'"

    def test_init_no_project_folder(self, temp_dir: str) -> None:
        """Test init with no project folder creation (deploy to current directory)."""
        # given
        os.chdir(temp_dir)

        # Mock subprocess for venv creation
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            # Mock subprocess to create venv directory when called
            def mock_subprocess_side_effect(*args, **kwargs):  # type: ignore
                if "venv" in str(args[0]):
                    venv_path = Path(temp_dir) / ".venv"
                    venv_path.mkdir(parents=True, exist_ok=True)
                    # Also create Scripts/bin directory for pip path checks
                    if os.name == "nt":
                        (venv_path / "Scripts").mkdir(exist_ok=True)
                    else:
                        (venv_path / "bin").mkdir(exist_ok=True)
                mock_result = MagicMock()
                mock_result.returncode = 0
                return mock_result

            mock_subprocess.side_effect = mock_subprocess_side_effect

            # when
            result = self.runner.invoke(
                fastkit_cli,
                ["init"],
                input="\n".join(
                    [
                        "test-project-no-folder",
                        "bnbong",
                        "bbbong9@gmail.com",
                        "test project",
                        "minimal",
                        "uv",
                        "Y",  # Proceed with project creation
                        "N",  # Do not create new project folder
                    ]
                ),
            )

        # then
        # Files should be deployed directly to temp_dir, not in a subfolder
        assert result.exit_code == 0
        assert "Success" in result.output

        # Check that main files exist directly in temp_dir
        main_py_paths = [Path(temp_dir) / "src" / "main.py", Path(temp_dir) / "main.py"]
        main_py_found = any(path.exists() for path in main_py_paths)
        assert main_py_found, "main.py should exist directly in current directory"

        # Check venv was created in current directory
        venv_path = Path(temp_dir) / ".venv"
        assert (
            venv_path.exists()
        ), "Virtual environment should be created in current directory"

        # Ensure no project folder was created
        project_folder = Path(temp_dir) / "test-project-no-folder"
        assert (
            not project_folder.exists()
        ), "Project folder should not be created when user selects 'N'"
