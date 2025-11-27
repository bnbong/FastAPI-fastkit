# --------------------------------------------------------------------------
# Test cases for CLI interactive mode integration
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from fastapi_fastkit.cli import fastkit_cli


class TestCLIInteractiveMode:
    """Test cases for interactive mode CLI operations."""

    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()

    def teardown_method(self, console: Any) -> None:
        os.chdir(self.current_workspace)

    def test_list_features_command(self, temp_dir: str) -> None:
        """Test fastkit list-features command."""
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(fastkit_cli, ["list-features"])

        # then
        assert result.exit_code == 0
        # Should display feature categories
        output_lower = result.output.lower()
        assert (
            "database" in output_lower
            or "authentication" in output_lower
            or "catalog" in output_lower
        )

    def test_init_interactive_command_exists(self, temp_dir: str) -> None:
        """Test that init --interactive command is recognized."""
        # given
        os.chdir(temp_dir)

        # when - just test that command doesn't error on --help
        result = self.runner.invoke(fastkit_cli, ["init", "--help"])

        # then
        assert result.exit_code == 0
        assert "--interactive" in result.output

    @patch("fastapi_fastkit.backend.package_managers.uv_manager.UvManager.is_available")
    @patch("subprocess.run")
    def test_init_interactive(
        self, mock_subprocess: MagicMock, mock_uv_available: MagicMock, temp_dir: str
    ) -> None:
        """Test init --interactive with real stack selections (PostgreSQL + JWT)."""
        # given
        os.chdir(temp_dir)
        project_name = "test-interactive-fullstack"
        author = "Interactive Test"
        author_email = "interactive@test.com"
        description = "Full-stack project via interactive mode"

        # Mock package manager as available and subprocess calls
        mock_uv_available.return_value = True
        mock_subprocess.return_value.returncode = 0

        # Mock subprocess to create venv directory when called
        def mock_subprocess_side_effect(*args: Any, **kwargs: Any) -> MagicMock:
            if "venv" in str(args[0]):
                venv_path = Path(temp_dir) / project_name / ".venv"
                venv_path.mkdir(parents=True, exist_ok=True)
                # Create Scripts/bin directory for pip path checks
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
            ["init", "--interactive"],
            input="\n".join(
                [
                    project_name,
                    author,
                    author_email,
                    description,
                    # Template selection removed - always Empty project
                    "1",  # Database: PostgreSQL (1st option)
                    "1",  # Authentication: JWT (1st option)
                    "1",  # Background Tasks: Celery (1st option)
                    "1",  # Caching: Redis (1st option)
                    "3",  # Monitoring: Prometheus (3rd option)
                    "1",  # Testing: Basic (1st option)
                    "1",  # Utilities: CORS (option 1)
                    "1",  # Deployment: Docker (1st option)
                    "2",  # Package manager: uv (2nd option)
                    "",  # Custom packages: skip
                    "Y",  # Proceed with project creation
                    "Y",  # Create project folder
                ]
            ),
        )

        # then
        project_path = Path(temp_dir) / project_name
        assert (
            project_path.exists() and project_path.is_dir()
        ), f"Project directory was not created. Output: {result.output}"

        # Check setup.py for project metadata
        setup_py = project_path / "setup.py"
        if setup_py.exists():
            with open(setup_py, "r") as f:
                setup_content = f.read()
                assert project_name in setup_content
                assert author in setup_content
                assert author_email in setup_content
                assert description in setup_content

        # Check dependency files for selected stack
        dependency_file_found = False
        deps_content = ""

        # Check pyproject.toml (for uv/poetry)
        if (project_path / "pyproject.toml").exists():
            dependency_file_found = True
            with open(project_path / "pyproject.toml", "r") as f:
                deps_content = f.read()
        # Check requirements.txt (for pip)
        elif (project_path / "requirements.txt").exists():
            dependency_file_found = True
            with open(project_path / "requirements.txt", "r") as f:
                deps_content = f.read()

        assert (
            dependency_file_found
        ), "No dependency file found (pyproject.toml or requirements.txt)"

        # Verify core dependencies
        deps_lower = deps_content.lower()
        assert "fastapi" in deps_lower, "fastapi should be in dependencies"
        assert "uvicorn" in deps_lower, "uvicorn should be in dependencies"

        # Verify selected stack dependencies based on interactive choices
        # Database: PostgreSQL
        assert (
            "psycopg2" in deps_lower
            or "asyncpg" in deps_lower
            or "sqlalchemy" in deps_lower
        ), "PostgreSQL dependencies (psycopg2/asyncpg/sqlalchemy) should be present"

        # Authentication: JWT
        assert (
            "python-jose" in deps_lower or "jose" in deps_lower or "pyjwt" in deps_lower
        ), "JWT authentication dependencies should be present"

        # Background Tasks: Celery
        assert "celery" in deps_lower, "Celery should be in dependencies"

        # Caching: Redis
        assert "redis" in deps_lower, "Redis should be in dependencies"

        # Monitoring: Prometheus
        assert (
            "prometheus" in deps_lower or "prometheus-client" in deps_lower
        ), "Prometheus monitoring dependencies should be present"

        # Testing: Basic (pytest)
        assert (
            "pytest" in deps_lower or "httpx" in deps_lower
        ), "Testing dependencies should be present"

        print(f"\n✅ Interactive mode created full-stack project successfully!")
        print(f"Project: {project_name}")
        print(f"Stack: PostgreSQL + JWT + Celery + Redis + Prometheus")
        print(f"Dependencies validated in pyproject.toml")

        # Check venv was created
        venv_path = project_path / ".venv"
        assert (
            venv_path.exists() and venv_path.is_dir()
        ), "Virtual environment should be created"

        # Check Docker files were created (deployment option 1 = Docker)
        dockerfile_path = project_path / "Dockerfile"
        assert (
            dockerfile_path.exists()
        ), "Dockerfile should be created when Docker deployment is selected"

        # Verify Dockerfile content
        with open(dockerfile_path, "r") as f:
            dockerfile_content = f.read()
            assert "FROM python:" in dockerfile_content
            assert "WORKDIR /app" in dockerfile_content
            assert "uvicorn" in dockerfile_content

        # Verify subprocess was called for venv and installation
        assert (
            mock_subprocess.call_count >= 2
        ), "subprocess should be called for venv creation and dependency installation"
