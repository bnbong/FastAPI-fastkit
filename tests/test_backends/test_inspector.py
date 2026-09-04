# --------------------------------------------------------------------------
# Testcases of inspector module.
#
# The inspector's individual checks are covered in test_inspector_checks.py;
# this module covers the TemplateInspector lifecycle, the static template
# checks, the test strategies and the public facade.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest

from fastapi_fastkit.backend.inspection import strategies as strategies_module
from fastapi_fastkit.backend.inspection.context import (
    InspectionContext,
    InspectionOptions,
)
from fastapi_fastkit.backend.inspection.docker import DockerCompose
from fastapi_fastkit.backend.inspector import (
    TemplateInspector,
    inspect_fastapi_template,
)

PYPROJECT_TPL = """
[project]
name = "<project_name>"
requires-python = ">=3.12"
dependencies = ["fastapi>=0.115.8", "uvicorn>=0.34.0"]

[tool.black]
target-version = ["py312"]

[tool.mypy]
python_version = "3.12"
"""

MAIN_TPL = """
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict:
    return {"Hello": "World"}
"""


class InspectorTestBase:
    """Shared synthetic template fixture."""

    def setup_method(self) -> None:
        self.temp_template_dir = tempfile.mkdtemp()
        self.template_path = Path(self.temp_template_dir)

    def teardown_method(self) -> None:
        import shutil

        if os.path.exists(self.temp_template_dir):
            shutil.rmtree(self.temp_template_dir)

    def create_valid_template_structure(self) -> None:
        """Create a template that satisfies every static check."""
        (self.template_path / "tests").mkdir(exist_ok=True)
        (self.template_path / "src").mkdir(exist_ok=True)

        (self.template_path / "requirements.txt-tpl").write_text(
            "fastapi==0.115.8\nuvicorn==0.34.0\n"
        )
        (self.template_path / "pyproject.toml-tpl").write_text(PYPROJECT_TPL)
        (self.template_path / "README.md-tpl").write_text("# Test Template")
        (self.template_path / "src" / "main.py-tpl").write_text(MAIN_TPL)
        (self.template_path / "tests" / "test_example.py-tpl").write_text(
            "def test_example() -> None:\n    assert True\n"
        )

    def make_inspector(
        self, temp_dir: str, options: Optional[InspectionOptions] = None
    ) -> TemplateInspector:
        """Build an inspector without entering the context manager."""
        return TemplateInspector(str(self.template_path), temp_dir, options)


class TestTemplateInspectorLifecycle(InspectorTestBase):
    """Construction, context management and cleanup."""

    def test_init_uses_template_specific_temp_dir(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()

        # when
        inspector = self.make_inspector(temp_dir)

        # then
        assert inspector.template_path == self.template_path
        assert inspector.temp_dir == os.path.join(
            temp_dir, f"temp_{self.template_path.name}"
        )
        assert inspector.errors == []
        assert inspector.warnings == []

    def test_init_defaults_temp_dir_to_backend_package(self) -> None:
        # given
        self.create_valid_template_structure()

        # when
        inspector = TemplateInspector(str(self.template_path))

        # then
        assert inspector.temp_dir.endswith(f"temp_{self.template_path.name}")
        assert os.path.basename(os.path.dirname(inspector.temp_dir)) == "backend"

    def test_context_manager_generates_project_and_cleans_up(
        self, temp_dir: str
    ) -> None:
        # given
        self.create_valid_template_structure()

        # when
        with self.make_inspector(temp_dir) as inspector:
            generated = inspector.temp_dir
            assert os.path.exists(generated)
            # placeholders are substituted during generation
            assert (
                "<project_name>"
                not in Path(os.path.join(generated, "pyproject.toml")).read_text()
            )

        # then
        assert not os.path.exists(generated)

    def test_context_manager_cleans_up_on_failure(self, temp_dir: str) -> None:
        """A generation failure removes the half-written project directory.

        The project is produced by the real ``ProjectScaffolder``, so the
        failure is injected at the template copy the scaffolder performs.
        """
        # given
        self.create_valid_template_structure()
        inspector = self.make_inspector(temp_dir)

        # when / then
        with patch(
            "fastapi_fastkit.backend.main.copy_and_convert_template",
            side_effect=OSError("copy failed"),
        ):
            with pytest.raises(OSError):
                inspector.__enter__()
        assert not os.path.exists(inspector.temp_dir)

    def test_generated_project_carries_fastkit_metadata(self, temp_dir: str) -> None:
        """Generation goes through the real scaffolder, markers included."""
        # given
        self.create_valid_template_structure()

        # when
        with self.make_inspector(temp_dir) as inspector:
            pyproject = Path(inspector.temp_dir) / "pyproject.toml"
            content = pyproject.read_text()

        # then
        assert "[tool.fastapi-fastkit]" in content
        assert "managed = true" in content

    def test_template_only_files_are_not_generated(self, temp_dir: str) -> None:
        """``template-config.yml`` drives inspection, never the user project."""
        # given
        self.create_valid_template_structure()
        (self.template_path / "template-config.yml-tpl").write_text("name: Demo\n")

        # when
        with self.make_inspector(temp_dir) as inspector:
            leaked = os.path.exists(
                os.path.join(inspector.temp_dir, "template-config.yml")
            )
            config = inspector.template_config

        # then
        assert not leaked
        assert config is not None and config["name"] == "Demo"

    def test_template_config_is_loaded_when_present(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()
        (self.template_path / "template-config.yml-tpl").write_text(
            "name: Demo\nrequires_docker: true\n"
        )

        # when
        with self.make_inspector(temp_dir) as inspector:
            config = inspector.template_config

        # then
        assert config is not None
        assert config["requires_docker"] is True

    def test_template_config_absent_yields_none(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()

        # when
        with self.make_inspector(temp_dir) as inspector:
            # then
            assert inspector.template_config is None


class TestStaticChecks(InspectorTestBase):
    """Structure, extension, dependency and implementation checks."""

    def test_file_structure_passes(self, temp_dir: str) -> None:
        self.create_valid_template_structure()
        inspector = self.make_inspector(temp_dir)
        assert inspector._check_file_structure() is True
        assert inspector.errors == []

    def test_file_structure_reports_missing_readme(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()
        (self.template_path / "README.md-tpl").unlink()

        # when / then
        inspector = self.make_inspector(temp_dir)
        assert inspector._check_file_structure() is False
        assert any("README.md-tpl" in error for error in inspector.errors)

    def test_file_structure_requires_metadata_file(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()
        (self.template_path / "pyproject.toml-tpl").unlink()

        # when / then
        inspector = self.make_inspector(temp_dir)
        assert inspector._check_file_structure() is False
        assert any("metadata file" in error for error in inspector.errors)

    def test_setup_py_only_template_still_passes(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()
        (self.template_path / "pyproject.toml-tpl").unlink()
        (self.template_path / "setup.py-tpl").write_text(
            "from setuptools import setup\nsetup(install_requires=['fastapi'])\n"
        )

        # when / then
        inspector = self.make_inspector(temp_dir)
        assert inspector._check_file_structure() is True
        assert inspector._check_dependencies() is True

    def test_file_extensions_reject_plain_py(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()
        (self.template_path / "src" / "leaked.py").write_text("x = 1\n")

        # when / then
        inspector = self.make_inspector(temp_dir)
        assert inspector._check_file_extensions() is False
        assert any("leaked.py" in error for error in inspector.errors)

    def test_dependencies_pass_from_pyproject_alone(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()
        (self.template_path / "requirements.txt-tpl").unlink()

        # when / then
        inspector = self.make_inspector(temp_dir)
        assert inspector._check_dependencies() is True

    def test_dependencies_fail_without_fastapi(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()
        (self.template_path / "requirements.txt-tpl").write_text("uvicorn==0.34.0\n")
        (self.template_path / "pyproject.toml-tpl").write_text(
            PYPROJECT_TPL.replace('"fastapi>=0.115.8", ', "")
        )

        # when / then
        inspector = self.make_inspector(temp_dir)
        assert inspector._check_dependencies() is False
        assert any("FastAPI dependency not found" in e for e in inspector.errors)

    def test_dependencies_fail_on_invalid_pyproject(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()
        (self.template_path / "pyproject.toml-tpl").write_text("not = = toml")

        # when / then
        inspector = self.make_inspector(temp_dir)
        assert inspector._check_dependencies() is False
        assert any("Invalid pyproject.toml-tpl" in e for e in inspector.errors)

    def test_fastapi_implementation_detects_app(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()

        # when / then
        with self.make_inspector(temp_dir) as inspector:
            assert inspector._check_fastapi_implementation() is True

    def test_fastapi_implementation_rejects_missing_main(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()

        # when / then
        with self.make_inspector(temp_dir) as inspector:
            with patch(
                "fastapi_fastkit.backend.inspection.checks.find_template_core_modules",
                return_value={"main": "", "setup": "", "pyproject": "", "config": ""},
            ):
                assert inspector._check_fastapi_implementation() is False
        assert any("main.py not found" in e for e in inspector.errors)

    def test_fastapi_implementation_rejects_module_without_app(
        self, temp_dir: str
    ) -> None:
        """A mere mention of FastAPI in a comment must not pass the check."""
        # given
        self.create_valid_template_structure()
        (self.template_path / "src" / "main.py-tpl").write_text(
            "# this module will host a FastAPI app one day\napp = 1\n"
        )

        # when / then
        with self.make_inspector(temp_dir) as inspector:
            assert inspector._check_fastapi_implementation() is False
        assert any("FastAPI app creation not found" in e for e in inspector.errors)


class TestStrategySelection:
    """Which strategy runs for which template configuration."""

    def _context(self, tmp_path: Path, config: Optional[Dict[str, Any]]) -> Any:
        return InspectionContext(
            template_path=tmp_path,
            temp_dir=str(tmp_path),
            template_config=config,
        )

    def test_standard_strategy_by_default(self, tmp_path: Path) -> None:
        strategy = strategies_module.select_strategy(self._context(tmp_path, None))
        assert isinstance(strategy, strategies_module.StandardStrategy)

    def test_docker_strategy_when_required(self, tmp_path: Path) -> None:
        strategy = strategies_module.select_strategy(
            self._context(tmp_path, {"requires_docker": True})
        )
        assert isinstance(strategy, strategies_module.DockerStrategy)

    def test_fallback_selected_when_configured(self, tmp_path: Path) -> None:
        strategy = strategies_module.select_fallback_strategy(
            self._context(tmp_path, {"fallback_testing": {"database_url": "sqlite://"}})
        )
        assert isinstance(strategy, strategies_module.FallbackStrategy)

    def test_fallback_degrades_to_standard(self, tmp_path: Path) -> None:
        strategy = strategies_module.select_fallback_strategy(
            self._context(tmp_path, {})
        )
        assert isinstance(strategy, strategies_module.StandardStrategy)

    def test_package_manager_detection(self, tmp_path: Path) -> None:
        assert strategies_module.detect_package_manager(str(tmp_path)) == "pip"
        (tmp_path / "pyproject.toml").write_text("[project]\n")
        assert strategies_module.detect_package_manager(str(tmp_path)) == "uv"


class TestStrategyExecution:
    """The shared strategy base: environment setup and result grading."""

    def _context(self, tmp_path: Path, config: Optional[Dict[str, Any]] = None) -> Any:
        venv = tmp_path / "venv" / "bin"
        venv.mkdir(parents=True)
        (venv / "python").write_text("")
        return InspectionContext(
            template_path=tmp_path,
            temp_dir=str(tmp_path),
            template_config=config,
            venv_path=str(tmp_path / "venv"),
        )

    def test_standard_strategy_passes_on_zero_exit(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        completed = subprocess.CompletedProcess(["pytest"], 0, "ok", "")

        # when
        with patch("subprocess.run", return_value=completed) as mock_run:
            result = strategies_module.StandardStrategy(ctx).run()

        # then
        assert result is True
        assert ctx.errors == []
        assert "-m" in mock_run.call_args[0][0]

    def test_standard_strategy_reports_failure_output(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        completed = subprocess.CompletedProcess(["pytest"], 1, "out", "err")

        # when
        with patch("subprocess.run", return_value=completed):
            result = strategies_module.StandardStrategy(ctx).run()

        # then
        assert result is False
        assert any("STDERR" in error and "err" in error for error in ctx.errors)

    def test_strategy_prefers_template_test_script(self, tmp_path: Path) -> None:
        # given
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "test.sh").write_text("#!/bin/sh\r\npytest\r\n")
        ctx = self._context(tmp_path)
        completed = subprocess.CompletedProcess(["test.sh"], 0, "", "")

        # when
        with patch("subprocess.run", return_value=completed) as mock_run:
            result = strategies_module.StandardStrategy(ctx).run()

        # then
        assert result is True
        assert mock_run.call_args[0][0] == [str(scripts_dir / "test.sh")]
        # line endings are normalised before execution
        assert b"\r\n" not in (scripts_dir / "test.sh").read_bytes()

    def test_strategy_reports_timeout(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)

        # when
        with patch(
            "subprocess.run", side_effect=subprocess.TimeoutExpired("pytest", 300)
        ):
            result = strategies_module.StandardStrategy(ctx).run()

        # then
        assert result is False
        assert any("timed out" in error for error in ctx.errors)

    def test_fallback_strategy_sets_database_url_and_warns(
        self, tmp_path: Path
    ) -> None:
        # given
        ctx = self._context(
            tmp_path,
            {
                "fallback_testing": {
                    "database_url": "sqlite:///:memory:",
                    "test_command": "pytest tests/ -q",
                }
            },
        )
        completed = subprocess.CompletedProcess(["pytest"], 0, "", "")

        # when
        with patch("subprocess.run", return_value=completed) as mock_run:
            result = strategies_module.FallbackStrategy(ctx).run()

        # then
        assert result is True
        env = mock_run.call_args.kwargs["env"]
        assert env["DATABASE_URL"] == "sqlite:///:memory:"
        assert mock_run.call_args[0][0][-3:] == ["pytest", "tests/", "-q"]
        assert any("fallback strategy" in w for w in ctx.warnings)

    def test_prepare_environment_reports_install_failure(self, tmp_path: Path) -> None:
        # given
        ctx = InspectionContext(template_path=tmp_path, temp_dir=str(tmp_path))

        # when
        with (
            patch.object(
                strategies_module, "create_venv", return_value=str(tmp_path / "venv")
            ),
            patch.object(
                strategies_module,
                "install_dependencies_with_manager",
                side_effect=RuntimeError("resolution failed"),
            ),
        ):
            result = strategies_module.prepare_environment(ctx)

        # then
        assert result is False
        assert any("Failed to install dependencies" in e for e in ctx.errors)

    def test_prepare_environment_is_idempotent(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)

        # when
        with patch.object(strategies_module, "create_venv") as mock_create:
            result = strategies_module.prepare_environment(ctx)

        # then
        assert result is True
        mock_create.assert_not_called()

    def test_disabled_tests_still_prepare_environment(self, tmp_path: Path) -> None:
        # given
        ctx = InspectionContext(
            template_path=tmp_path,
            temp_dir=str(tmp_path),
            options=InspectionOptions(run_template_tests=False),
        )

        # when
        with patch.object(
            strategies_module, "prepare_environment", return_value=True
        ) as mock_prepare:
            result = strategies_module.run_template_tests(ctx)

        # then
        assert result is True
        mock_prepare.assert_called_once_with(ctx)


class TestDockerStrategy:
    """Docker orchestration is fully mocked - no daemon is required."""

    def _context(self, tmp_path: Path) -> Any:
        return InspectionContext(
            template_path=tmp_path,
            temp_dir=str(tmp_path),
            template_config={
                "requires_docker": True,
                "testing": {"compose_file": "docker-compose.yml"},
                "test_env_defaults": {"POSTGRES_USER": "test_user"},
            },
        )

    def test_falls_back_when_docker_missing(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        ctx.template_config = dict(ctx.template_config or {})
        ctx.template_config["fallback_testing"] = {"database_url": "sqlite://"}

        # when
        with (
            patch.object(DockerCompose, "is_available", return_value=False),
            patch.object(
                strategies_module.FallbackStrategy, "run", return_value=True
            ) as mock_run,
        ):
            result = strategies_module.DockerStrategy(ctx).run()

        # then
        assert result is True
        mock_run.assert_called_once()
        assert any("Docker not available" in w for w in ctx.warnings)

    def test_successful_docker_run(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        compose = MagicMock()
        compose.containers_running.return_value = False
        compose.up.return_value = subprocess.CompletedProcess(["up"], 0, "", "")
        compose.verify_services_running.return_value = None
        compose.exec_tests.return_value = subprocess.CompletedProcess(
            ["pytest"], 0, "", ""
        )

        # when
        with (
            patch.object(DockerCompose, "is_available", return_value=True),
            patch.object(strategies_module, "DockerCompose", return_value=compose),
        ):
            result = strategies_module.DockerStrategy(ctx).run()

        # then
        assert result is True
        compose.cleanup.assert_called_once()
        # test_env_defaults are materialised into a .env file
        assert "POSTGRES_USER=test_user" in (tmp_path / ".env").read_text()

    def test_service_verification_failure_is_reported(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        compose = MagicMock()
        compose.containers_running.return_value = True
        compose.verify_services_running.return_value = "Database service is not running"

        # when
        with (
            patch.object(DockerCompose, "is_available", return_value=True),
            patch.object(strategies_module, "DockerCompose", return_value=compose),
        ):
            result = strategies_module.DockerStrategy(ctx).run()

        # then
        assert result is False
        assert "Database service is not running" in ctx.errors

    def test_failed_startup_is_reported(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        compose = MagicMock()
        compose.containers_running.return_value = False
        compose.up.return_value = subprocess.CompletedProcess(
            ["up"], 1, "", "no such image"
        )

        # when
        with (
            patch.object(DockerCompose, "is_available", return_value=True),
            patch.object(strategies_module, "DockerCompose", return_value=compose),
        ):
            result = strategies_module.DockerStrategy(ctx).run()

        # then
        assert result is False
        assert any("Failed to start Docker services" in e for e in ctx.errors)


class TestDockerCompose:
    """The compose wrapper's own process handling."""

    def test_is_available_false_without_binaries(self) -> None:
        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert DockerCompose.is_available() is False

    def test_is_available_true_when_both_respond(self) -> None:
        completed = subprocess.CompletedProcess(["docker"], 0, "v1", "")
        with patch("subprocess.run", return_value=completed):
            assert DockerCompose.is_available() is True

    def test_containers_running_false_without_containers(self, tmp_path: Path) -> None:
        completed = subprocess.CompletedProcess(["ps"], 0, "\n", "")
        with patch("subprocess.run", return_value=completed):
            assert DockerCompose(str(tmp_path)).containers_running() is False

    def test_verify_services_running_detects_missing_app(self, tmp_path: Path) -> None:
        # given
        payload = '{"Name": "demo-db-1", "State": "running"}'
        completed = subprocess.CompletedProcess(["ps"], 0, payload, "")

        # when
        with patch("subprocess.run", return_value=completed):
            error = DockerCompose(str(tmp_path)).verify_services_running()

        # then
        assert error is not None and "Application service" in error


class TestReportAndFacade(InspectorTestBase):
    """Report shape and the inspect_fastapi_template entry point."""

    def test_report_is_valid_without_errors(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()
        inspector = self.make_inspector(temp_dir)

        # when
        report = inspector.get_report()

        # then
        assert report["is_valid"] is True
        assert report["errors"] == []
        assert report["template_path"] == str(self.template_path)

    def test_report_is_invalid_with_errors(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()
        inspector = self.make_inspector(temp_dir)
        inspector.ctx.add_error("boom")
        inspector.ctx.add_warning("careful")

        # when
        report = inspector.get_report()

        # then
        assert report["is_valid"] is False
        assert report["errors"] == ["boom"]
        assert report["warnings"] == ["careful"]

    def test_inspect_fastapi_template_returns_report(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()

        # when
        with patch.object(TemplateInspector, "inspect_template", return_value=True):
            report = inspect_fastapi_template(str(self.template_path), temp_dir)

        # then
        assert report["is_valid"] is True
        assert report["template_path"] == str(self.template_path)

    def test_inspect_fastapi_template_surfaces_errors(self, temp_dir: str) -> None:
        # given
        self.create_valid_template_structure()

        def fail(self: TemplateInspector) -> bool:
            self.ctx.add_error("check failed")
            return False

        # when
        with patch.object(TemplateInspector, "inspect_template", fail):
            report = inspect_fastapi_template(str(self.template_path), temp_dir)

        # then
        assert report["is_valid"] is False
        assert report["errors"] == ["check failed"]

    def test_inspect_template_stops_at_first_failure(self, temp_dir: str) -> None:
        # given: a template without a README fails the very first check
        self.create_valid_template_structure()
        (self.template_path / "README.md-tpl").unlink()

        # when
        with self.make_inspector(temp_dir) as inspector:
            with patch.object(
                TemplateInspector, "_test_template", return_value=True
            ) as mock_tests:
                result = inspector.inspect_template()

        # then
        assert result is False
        mock_tests.assert_not_called()

    def test_inspect_template_runs_every_check(self, temp_dir: str) -> None:
        # given: all expensive steps stubbed out
        self.create_valid_template_structure()
        options = InspectionOptions(
            offline=True, run_smoke_test=False, run_template_tests=False
        )

        # when
        with self.make_inspector(temp_dir, options) as inspector:
            with patch.object(
                strategies_module, "prepare_environment", return_value=True
            ):
                result = inspector.inspect_template()

        # then
        assert result is True, inspector.errors
        assert inspector.errors == []
