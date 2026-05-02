# --------------------------------------------------------------------------
# Test cases for CLI interactive mode integration
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
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

    def test_init_help_mentions_architecture_preset(self, temp_dir: str) -> None:
        """``fastkit init --help`` must call out the new preset step.

        Regression guard for issue #44's "docs/help text reflect the new
        step" acceptance criterion — keeps the user-facing help in sync
        with the actual interactive flow.
        """
        # given / when
        result = self.runner.invoke(fastkit_cli, ["init", "--help"])

        # then
        assert result.exit_code == 0
        text = result.output.lower()
        assert "architecture preset" in text or "architecture" in text
        # The four canonical preset ids must all be discoverable from --help.
        for preset_id in (
            "minimal",
            "single-module",
            "classic-layered",
            "domain-starter",
        ):
            assert preset_id in text, (
                f"expected preset id {preset_id!r} in init --help output, "
                f"got:\n{result.output}"
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
                    "",  # Architecture preset: accept default (domain-starter)
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

        print("\n✅ Interactive mode created full-stack project successfully!")
        print(f"Project: {project_name}")
        print("Stack: PostgreSQL + JWT + Celery + Redis + Prometheus")
        print("Dependencies validated in pyproject.toml")

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

        # Pytest config must land in pytest.ini, not overwrite tests/conftest.py
        # (INI content in a Python module breaks the entire test suite).
        pytest_ini = project_path / "pytest.ini"
        assert pytest_ini.exists(), "Generated project should have a pytest.ini"
        ini_content = pytest_ini.read_text()
        assert "[pytest]" in ini_content

        conftest_path = project_path / "tests" / "conftest.py"
        if conftest_path.exists():
            conftest_content = conftest_path.read_text()
            assert (
                "[pytest]" not in conftest_content
            ), "conftest.py must remain a Python module, not INI content"

        # Verify subprocess was called for venv and installation
        assert (
            mock_subprocess.call_count >= 2
        ), "subprocess should be called for venv creation and dependency installation"

    @patch("fastapi_fastkit.cli.create_venv_with_manager")
    @patch("fastapi_fastkit.backend.package_managers.uv_manager.UvManager.is_available")
    def test_init_interactive_cleans_up_on_failure(
        self,
        mock_uv_available: MagicMock,
        mock_create_venv: MagicMock,
        temp_dir: str,
    ) -> None:
        """When interactive init fails, the partial project folder must be removed."""
        # given
        os.chdir(temp_dir)
        project_name = "test-interactive-failure"
        mock_uv_available.return_value = True
        mock_create_venv.side_effect = RuntimeError(
            "simulated venv failure for cleanup test"
        )

        # when: reuse the same selections as the happy-path test so only the
        # patched create_venv_with_manager triggers the failure branch
        result = self.runner.invoke(
            fastkit_cli,
            ["init", "--interactive"],
            input="\n".join(
                [
                    project_name,
                    "Failure Test",
                    "failure@test.com",
                    "Triggers interactive cleanup branch",
                    "",  # Architecture preset: accept default (domain-starter)
                    "1",  # Database: PostgreSQL
                    "1",  # Authentication: JWT
                    "1",  # Background Tasks: Celery
                    "1",  # Caching: Redis
                    "3",  # Monitoring: Prometheus
                    "1",  # Testing: Basic
                    "1",  # Utilities: CORS
                    "1",  # Deployment: Docker
                    "2",  # Package manager: uv
                    "",  # Custom packages: skip
                    "Y",  # Proceed
                    "Y",  # Create project folder
                ]
            ),
        )

        # then: the except block ran
        assert (
            "Error during project creation" in result.output
        ), f"Expected cleanup branch to print error. Output: {result.output}"
        assert "simulated venv failure" in result.output

        # and: the partially-created project folder was cleaned up
        project_path = Path(temp_dir) / project_name
        assert (
            not project_path.exists()
        ), "Failed interactive init must leave no partial project folder"

    # Each tuple: (preset prompt input, project name suffix,
    #              base template marker, marker file produced by the preset's
    #              base template, dynamic db config target relative path,
    #              should the dynamic main.py overlay overwrite the shipped one).
    _PRESET_LAYOUT_CASES = [
        (
            "1",
            "minimal",
            "fastapi-empty",
            "src/main.py",
            "src/config/database.py",
            True,
        ),
        (
            "2",
            "single-module",
            "fastapi-single-module",
            "src/main.py",
            "src/config/database.py",
            True,
        ),
        (
            "3",
            "classic-layered",
            "fastapi-default",
            "src/main.py",
            "src/core/database.py",
            False,
        ),
        (
            "4",
            "domain-starter",
            "fastapi-domain-starter",
            "src/app/main.py",
            "src/app/core/database.py",
            False,
        ),
    ]

    @pytest.mark.parametrize(
        "preset_choice,suffix,base_template_name,main_relpath,db_relpath,regenerates_main",
        _PRESET_LAYOUT_CASES,
        ids=[case[1] for case in _PRESET_LAYOUT_CASES],
    )
    @patch("fastapi_fastkit.cli.subprocess.run")
    @patch("fastapi_fastkit.backend.package_managers.uv_manager.UvManager.is_available")
    def test_init_interactive_layout_per_preset(
        self,
        mock_uv_available: MagicMock,
        mock_subprocess: MagicMock,
        temp_dir: str,
        preset_choice: str,
        suffix: str,
        base_template_name: str,
        main_relpath: str,
        db_relpath: str,
        regenerates_main: bool,
    ) -> None:
        """Each architecture preset deploys a different base template and
        writes generated database config into the preset-specific path.

        The dynamic main.py overlay only replaces the shipped main.py for
        presets that opt in (minimal, single-module); the richer presets
        (classic-layered, domain-starter) preserve the template-shipped
        main.py as a sentinel that we don't clobber router-aware code.
        """
        # given
        os.chdir(temp_dir)
        project_name = f"layout-{suffix}"

        mock_uv_available.return_value = True

        def _mock_subprocess(*args: Any, **kwargs: Any) -> MagicMock:
            if args and "venv" in str(args[0]):
                venv_path = Path(temp_dir) / project_name / ".venv"
                venv_path.mkdir(parents=True, exist_ok=True)
                bin_dir = "Scripts" if os.name == "nt" else "bin"
                (venv_path / bin_dir).mkdir(exist_ok=True)
            mock_result = MagicMock()
            mock_result.returncode = 0
            return mock_result

        mock_subprocess.side_effect = _mock_subprocess

        # Pick a feature combination that triggers warnings on richer
        # presets (CORS + Prometheus) so the same input string exercises
        # both code paths.
        result = self.runner.invoke(
            fastkit_cli,
            ["init", "--interactive"],
            input="\n".join(
                [
                    project_name,
                    "Layout Tester",
                    "layout@test.com",
                    f"Layout regression for {suffix}",
                    preset_choice,  # Architecture preset
                    "1",  # Database: PostgreSQL
                    "5",  # Authentication: None (last option)
                    "3",  # Background Tasks: None (last option)
                    "2",  # Caching: None (last option)
                    "3",  # Monitoring: Prometheus
                    "1",  # Testing: Basic
                    "1",  # Utilities: CORS
                    "3",  # Deployment: None
                    "2",  # Package manager: uv
                    "",  # Custom packages: skip
                    "Y",  # Proceed
                    "Y",  # Create project folder
                ]
            ),
        )

        # then
        project_path = Path(temp_dir) / project_name
        assert project_path.exists() and project_path.is_dir(), (
            f"[{suffix}] project not created. exit_code={result.exit_code}\n"
            f"output:\n{result.output}"
        )

        # The base template's signature file ends up in the project, which
        # is how we tell that the strategist picked the right template.
        main_py = project_path / main_relpath
        assert main_py.exists(), (
            f"[{suffix}] expected main.py at {main_relpath}; not found.\n"
            f"output:\n{result.output}"
        )

        # Database config lands at the preset-specific target path.
        db_config = project_path / db_relpath
        assert db_config.exists(), (
            f"[{suffix}] expected generated db config at {db_relpath}; "
            f"contents:\n{list(project_path.rglob('*'))}"
        )

        # Dynamic main.py marker is the FastAPI-fastkit header comment
        # that ``DynamicConfigGenerator.generate_main_py`` always emits.
        # Presence/absence is the contract: regenerated for minimal /
        # single-module, preserved for classic-layered / domain-starter.
        main_text = main_py.read_text()
        if regenerates_main:
            assert "Generated by FastAPI-fastkit" in main_text, (
                f"[{suffix}] main.py was not regenerated by the dynamic "
                f"overlay. content head:\n{main_text[:400]}"
            )
        else:
            assert "Generated by FastAPI-fastkit" not in main_text, (
                f"[{suffix}] template-shipped main.py was overwritten by "
                f"the dynamic overlay; preserve-main contract violated. "
                f"content head:\n{main_text[:400]}"
            )

        # Compatibility warnings only fire on preserve-main presets, and
        # only for selections whose dynamic main.py overlay isn't applied.
        # CORS is pre-wired in the shipped main.py for both preserve-main
        # presets, so the warning must NOT mention it — it should mention
        # Prometheus (selected above) which truly does need manual wiring.
        if regenerates_main:
            assert "Preset compatibility" not in result.output, (
                f"[{suffix}] unexpected compatibility warning. "
                f"output:\n{result.output}"
            )
        else:
            assert "Preset compatibility" in result.output, (
                f"[{suffix}] expected a 'Preset compatibility' warning for "
                f"Prometheus on a preserve-main preset.\n"
                f"output:\n{result.output}"
            )
            assert "Prometheus" in result.output, (
                f"[{suffix}] warning must list Prometheus.\n"
                f"output:\n{result.output}"
            )
            # The warning's "affected selections" line lists each affected
            # feature individually; CORS must not appear there because it
            # is already wired in the shipped main.py.
            warning_section = result.output.split("Preset compatibility", 1)[1]
            affected_line = next(
                (
                    line
                    for line in warning_section.splitlines()
                    if "Affected selections" in line
                ),
                "",
            )
            assert affected_line, (
                f"[{suffix}] expected an 'Affected selections' line.\n"
                f"output:\n{result.output}"
            )
            assert "CORS" not in affected_line, (
                f"[{suffix}] CORS must NOT appear in the affected-selections "
                f"line — it is pre-wired in the shipped main.py.\n"
                f"output:\n{result.output}"
            )
