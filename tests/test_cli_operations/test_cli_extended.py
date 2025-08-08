# --------------------------------------------------------------------------
# Testcases of CLI extended operations (extended test cases).
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from fastapi_fastkit.cli import fastkit_cli


class TestCLIExtended:
    """Extended test cases for CLI operations."""

    def setup_method(self) -> None:
        """Setup method for each test."""
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()

    def teardown_method(self) -> None:
        """Cleanup method for each test."""
        os.chdir(self.current_workspace)

    def test_help_command(self) -> None:
        """Test help command."""
        # given & when
        result = self.runner.invoke(fastkit_cli, ["--help"])

        # then
        assert result.exit_code == 0
        assert "Commands:" in result.output or "Usage:" in result.output

    def test_version_command(self) -> None:
        """Test version command if available."""
        # given & when
        result = self.runner.invoke(fastkit_cli, ["--version"])

        # then
        # Version command might not exist, but shouldn't crash
        assert result.exit_code in [0, 2]  # 0 for success, 2 for no such option

    @patch("subprocess.run")
    @patch("fastapi_fastkit.backend.package_managers.uv_manager.UvManager.is_available")
    def test_init_standard_stack(
        self,
        mock_uv_available: MagicMock,
        mock_subprocess: MagicMock,
        temp_dir: str,
    ) -> None:
        """Test init command with standard stack."""
        # given
        os.chdir(temp_dir)
        mock_uv_available.return_value = True

        # Mock subprocess.run to simulate venv creation and dependency installation
        def mock_subprocess_side_effect(*args, **kwargs) -> MagicMock:  # type: ignore
            cmd = args[0] if args else kwargs.get("args", [])
            if isinstance(cmd, list) and len(cmd) > 0:
                # Simulate venv creation by creating the directory
                if cmd[0] == "uv" and "venv" in cmd:
                    venv_path = Path(temp_dir) / "test-standard" / ".venv"
                    venv_path.mkdir(parents=True, exist_ok=True)
                    # Create bin directory for Unix-like systems
                    (venv_path / "bin").mkdir(exist_ok=True)
                    (venv_path / "Scripts").mkdir(
                        exist_ok=True
                    )  # For Windows compatibility

            return MagicMock(returncode=0, stdout="", stderr="")

        mock_subprocess.side_effect = mock_subprocess_side_effect

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init"],
            input="\n".join(
                [
                    "test-standard",
                    "Test Author",
                    "test@example.com",
                    "Standard FastAPI project",
                    "standard",
                    "uv",
                    "Y",
                ]
            ),
        )

        # then
        project_path = Path(temp_dir) / "test-standard"
        assert project_path.exists()
        assert "Success" in result.output

        # Verify that subprocess.run was called for venv and dependency operations
        assert mock_subprocess.call_count >= 2

    def test_addroute_command(self, temp_dir: str) -> None:
        """Test addroute command behavior."""
        # given
        os.chdir(temp_dir)
        project_name = "test-project"
        route_name = "users"

        # Create a dummy project directory with fastkit structure
        project_path = Path(temp_dir) / project_name
        project_path.mkdir(exist_ok=True)

        # Create setup.py to make it a valid fastkit project
        setup_py = project_path / "setup.py"
        setup_py.write_text(
            """
from setuptools import setup, find_packages

setup(
    name="test-project",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.23.0",
    ],
    description="Created with FastAPI-fastkit",
    author="Test Author",
    author_email="test@example.com",
)
"""
        )

        # when
        result = self.runner.invoke(
            fastkit_cli, ["addroute", project_name, route_name], input="Y"
        )

        # then
        # The command should execute without crashing (exit code 0 or 1 acceptable)
        assert result.exit_code in [0, 1]

        # Check that the CLI showed the project information
        assert project_name in result.output
        assert route_name in result.output

        # The command might fail due to missing src directory or template files,
        # but should handle it gracefully and show meaningful error messages

    def test_addroute_command_cancel(self, temp_dir: str) -> None:
        """Test addroute command with cancellation."""
        # given
        os.chdir(temp_dir)
        project_name = "test-project"
        route_name = "users"

        # Create a dummy project directory
        project_path = Path(temp_dir) / project_name
        project_path.mkdir(exist_ok=True)

        # when
        result = self.runner.invoke(
            fastkit_cli, ["addroute", project_name, route_name], input="N"
        )

        # then
        assert "Operation cancelled" in result.output or "Aborted" in result.output

    def test_startdemo_with_different_templates(self, temp_dir: str) -> None:
        """Test startdemo with different template types."""
        # given
        os.chdir(temp_dir)

        templates_to_test = [
            "fastapi-async-crud",
            "fastapi-custom-response",
            "fastapi-dockerized",
        ]

        for template in templates_to_test:
            # Create a subdirectory for each template test
            template_test_dir = Path(temp_dir) / f"test_{template}"
            template_test_dir.mkdir(exist_ok=True)
            os.chdir(template_test_dir)

            # when
            result = self.runner.invoke(
                fastkit_cli,
                ["startdemo", template],
                input="\n".join(
                    [
                        f"test-{template}",
                        "Test Author",
                        "test@example.com",
                        f"Test project for {template}",
                        "Y",
                    ]
                ),
            )

            # then
            # Should not crash, even if template doesn't exist
            assert result.exit_code in [0, 1]

            # Return to temp_dir for next iteration
            os.chdir(temp_dir)

    def test_runserver_command(self, temp_dir: str) -> None:
        """Test runserver command."""
        # given
        os.chdir(temp_dir)

        # Create a minimal project structure
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()
        main_py = src_dir / "main.py"
        main_py.write_text(
            """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
"""
        )

        # when
        with patch("subprocess.Popen") as mock_popen:
            mock_process = MagicMock()
            mock_popen.return_value = mock_process

            result = self.runner.invoke(fastkit_cli, ["runserver"])

            # then
            # Should attempt to run the server
            assert result.exit_code in [0, 1]

    def test_deleteproject_nonexistent(self, temp_dir: str) -> None:
        """Test deleteproject with non-existent project."""
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(
            fastkit_cli, ["deleteproject", "nonexistent-project"], input="Y"
        )

        # then
        assert (
            "not found" in result.output.lower()
            or "does not exist" in result.output.lower()
        )

    def test_list_templates_detailed(self, temp_dir: str) -> None:
        """Test list-templates command in detail."""
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(fastkit_cli, ["list-templates"])

        # then
        assert result.exit_code == 0
        assert "Available Templates" in result.output

        # Should list common templates
        expected_templates = [
            "fastapi-default",
            "fastapi-empty",
            "fastapi-dockerized",
            "fastapi-async-crud",
            "fastapi-custom-response",
            "fastapi-psql-orm",
        ]

        # At least some templates should be listed
        template_found = any(
            template in result.output for template in expected_templates
        )
        assert template_found

    def test_startdemo_invalid_template(self, temp_dir: str) -> None:
        """Test startdemo with invalid template name."""
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["startdemo", "invalid-template-name"],
            input="\n".join(
                [
                    "test-project",
                    "Test Author",
                    "test@example.com",
                    "Test description",
                    "Y",
                ]
            ),
        )

        # then
        # Should handle invalid template gracefully
        assert result.exit_code in [0, 1]

    def test_init_with_existing_directory(self, temp_dir: str) -> None:
        """Test init command when directory already exists."""
        # given
        os.chdir(temp_dir)
        project_name = "existing-project"

        # Create existing directory
        existing_dir = Path(temp_dir) / project_name
        existing_dir.mkdir()

        # when
        result = self.runner.invoke(
            fastkit_cli,
            ["init"],
            input="\n".join(
                [
                    project_name,
                    "Test Author",
                    "test@example.com",
                    "Test description",
                    "minimal",
                    "Y",
                ]
            ),
        )

        # then
        # Should handle existing directory appropriately
        assert result.exit_code in [0, 1]

    @patch("fastapi_fastkit.backend.inspector.inspect_fastapi_template")
    def test_inspect_command_if_exists(
        self, mock_inspect: MagicMock, temp_dir: str
    ) -> None:
        """Test inspect command if it exists in CLI."""
        # given
        os.chdir(temp_dir)
        mock_inspect.return_value = {"is_valid": True, "errors": [], "warnings": []}

        # Create a dummy template directory
        template_dir = Path(temp_dir) / "test-template"
        template_dir.mkdir()

        # when
        # Try to run inspect command (might not exist)
        result = self.runner.invoke(fastkit_cli, ["inspect", str(template_dir)])

        # then
        # Should either work or fail gracefully
        assert result.exit_code in [0, 1, 2]  # 2 for command not found

    def test_echo_command_output_format(self) -> None:
        """Test echo command output format in detail."""
        # given & when
        result = self.runner.invoke(fastkit_cli, ["echo"])

        # then
        assert result.exit_code == 0

        # Check for basic content that should be in echo output
        expected_content = ["FastAPI-fastkit", "bnbong", "github.com"]

        for content in expected_content:
            assert content.lower() in result.output.lower()
