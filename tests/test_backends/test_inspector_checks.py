# --------------------------------------------------------------------------
# Testcases for the individual template inspection checks.
#
# Each check is exercised against a synthetic template/generated-project pair
# built in a tmp_path, so the checks are validated independently of the
# TemplateInspector lifecycle.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest

from fastapi_fastkit.backend.inspection import checks, consistency, freshness, lint
from fastapi_fastkit.backend.inspection import smoke as smoke_module
from fastapi_fastkit.backend.inspection.context import (
    InspectionContext,
    InspectionOptions,
)

VALID_PYPROJECT = """
[project]
name = "demo"
requires-python = ">=3.12"
dependencies = ["fastapi>=0.115.8", "uvicorn>=0.34.0"]

[tool.black]
target-version = ["py312"]

[tool.mypy]
python_version = "3.12"
"""

VALID_REQUIREMENTS = "fastapi==0.115.8\nuvicorn==0.34.0\n"


def make_context(
    tmp_path: Path,
    pyproject: Optional[str] = VALID_PYPROJECT,
    requirements: Optional[str] = VALID_REQUIREMENTS,
    options: Optional[InspectionOptions] = None,
) -> InspectionContext:
    """Build a context over a synthetic template + generated project pair."""
    template_dir = tmp_path / "template"
    generated_dir = tmp_path / "generated"
    (template_dir / "tests").mkdir(parents=True)
    generated_dir.mkdir()

    (template_dir / "README.md-tpl").write_text("# Demo")
    (template_dir / "tests" / "test_demo.py-tpl").write_text("def test_ok(): ...\n")
    if pyproject is not None:
        (template_dir / "pyproject.toml-tpl").write_text(pyproject)
        (generated_dir / "pyproject.toml").write_text(pyproject)
    if requirements is not None:
        (template_dir / "requirements.txt-tpl").write_text(requirements)

    return InspectionContext(
        template_path=template_dir,
        temp_dir=str(generated_dir),
        options=options or InspectionOptions(),
    )


class TestTestSuitePresenceCheck:
    """A template without tests is a hard failure, not a warning."""

    def test_passes_with_test_module(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)

        # when / then
        assert checks.check_tests_present(ctx) is True
        assert ctx.errors == []

    def test_fails_without_tests_directory(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        (ctx.template_path / "tests" / "test_demo.py-tpl").unlink()
        (ctx.template_path / "tests").rmdir()

        # when / then
        assert checks.check_tests_present(ctx) is False
        assert any("tests" in error for error in ctx.errors)

    def test_fails_with_empty_tests_directory(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        (ctx.template_path / "tests" / "test_demo.py-tpl").unlink()

        # when / then
        assert checks.check_tests_present(ctx) is False
        assert any("No test module" in error for error in ctx.errors)


class TestJunkFileCheck:
    """OS and build artifacts must not ship inside a template."""

    def test_passes_on_clean_template(self, tmp_path: Path) -> None:
        ctx = make_context(tmp_path)
        assert checks.check_no_junk_files(ctx) is True

    @pytest.mark.parametrize("junk_name", [".DS_Store", "Thumbs.db", "stale.pyc"])
    def test_fails_on_junk_file(self, tmp_path: Path, junk_name: str) -> None:
        # given
        ctx = make_context(tmp_path)
        (ctx.template_path / junk_name).write_text("")

        # when / then
        assert checks.check_no_junk_files(ctx) is False
        assert any(junk_name in error for error in ctx.errors)

    def test_fails_on_pycache_directory(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        (ctx.template_path / "__pycache__").mkdir()

        # when / then
        assert checks.check_no_junk_files(ctx) is False


class TestPlaceholderResidueCheck:
    """Generation must substitute every placeholder token."""

    def test_passes_on_substituted_project(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        Path(ctx.temp_path("README.md")).write_text("# demo project")

        # when / then
        assert checks.check_no_placeholder_residue(ctx) is True

    def test_fails_on_residual_placeholder(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        Path(ctx.temp_path("README.md")).write_text("# <project_name> by <author>")

        # when / then
        assert checks.check_no_placeholder_residue(ctx) is False
        assert any("<project_name>" in error for error in ctx.errors)


class TestConfigurationConsistencyCheck:
    """Python version pins must agree and dependency lists must not drift."""

    def test_passes_on_consistent_template(self, tmp_path: Path) -> None:
        ctx = make_context(tmp_path)
        assert consistency.check_configuration_consistency(ctx) is True
        assert ctx.errors == []

    def test_fails_on_old_requires_python(self, tmp_path: Path) -> None:
        # given
        pyproject = VALID_PYPROJECT.replace('">=3.12"', '">=3.9"')
        ctx = make_context(tmp_path, pyproject=pyproject)

        # when / then
        assert consistency.check_configuration_consistency(ctx) is False
        assert any("requires-python" in error for error in ctx.errors)

    def test_fails_on_black_target_version_drift(self, tmp_path: Path) -> None:
        # given
        pyproject = VALID_PYPROJECT.replace('["py312"]', '["py39"]')
        ctx = make_context(tmp_path, pyproject=pyproject)

        # when / then
        assert consistency.check_configuration_consistency(ctx) is False
        assert any("target-version" in error for error in ctx.errors)

    def test_fails_on_mypy_python_version_drift(self, tmp_path: Path) -> None:
        # given
        pyproject = VALID_PYPROJECT.replace(
            'python_version = "3.12"', 'python_version = "3.9"'
        )
        ctx = make_context(tmp_path, pyproject=pyproject)

        # when / then
        assert consistency.check_configuration_consistency(ctx) is False
        assert any("python_version" in error for error in ctx.errors)

    def test_fails_on_dependency_drift(self, tmp_path: Path) -> None:
        # given: requirements.txt-tpl lost a dependency pyproject still declares
        ctx = make_context(tmp_path, requirements="fastapi==0.115.8\n")

        # when / then
        assert consistency.check_configuration_consistency(ctx) is False
        assert any("Dependency drift" in error for error in ctx.errors)

    def test_fails_when_fastkit_is_a_runtime_dependency(self, tmp_path: Path) -> None:
        # given
        pyproject = VALID_PYPROJECT.replace(
            '"uvicorn>=0.34.0"', '"uvicorn>=0.34.0", "fastapi-fastkit>=1.1.5"'
        )
        requirements = VALID_REQUIREMENTS + "FastAPI-fastkit==1.1.5\n"
        ctx = make_context(tmp_path, pyproject=pyproject, requirements=requirements)

        # when / then
        assert consistency.check_configuration_consistency(ctx) is False
        assert any("must not be a runtime dependency" in error for error in ctx.errors)


class TestLintChecks:
    """compileall is mandatory; mypy is opt-in."""

    def test_compileall_passes_on_valid_module(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        Path(ctx.temp_path("main.py")).write_text("value = 1\n")

        # when / then
        assert lint.check_compileall(ctx) is True

    def test_compileall_fails_on_syntax_error(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        Path(ctx.temp_path("broken.py")).write_text("def broken(:\n")

        # when / then
        assert lint.check_compileall(ctx) is False
        assert any("failed to compile" in error for error in ctx.errors)

    def test_mypy_skipped_when_disabled(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, options=InspectionOptions(run_mypy=False))

        # when
        with patch("subprocess.run") as mock_run:
            result = lint.check_mypy(ctx)

        # then
        assert result is True
        mock_run.assert_not_called()

    def test_mypy_reports_errors_when_enabled(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, options=InspectionOptions(run_mypy=True))
        completed = subprocess.CompletedProcess(
            args=["mypy"], returncode=1, stdout="main.py:1: error: bad", stderr=""
        )

        # when
        with patch("subprocess.run", return_value=completed):
            result = lint.check_mypy(ctx)

        # then
        assert result is False
        assert any("mypy reported errors" in error for error in ctx.errors)


class TestDependencyFreshnessCheck:
    """Freshness lookups are advisory and always skippable."""

    def test_offline_mode_skips_network(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, options=InspectionOptions(offline=True))

        # when
        with patch.object(freshness, "fetch_latest_version") as mock_fetch:
            result = freshness.check_dependency_freshness(ctx)

        # then
        assert result is True
        mock_fetch.assert_not_called()
        assert ctx.warnings == []

    def test_warns_on_major_version_lag(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, requirements="fastapi==0.115.8\n", pyproject=None)

        # when
        with patch.object(freshness, "fetch_latest_version", return_value="1.2.0"):
            result = freshness.check_dependency_freshness(ctx)

        # then
        assert result is True
        assert any("major version(s) behind" in warning for warning in ctx.warnings)

    def test_warns_on_minor_version_lag(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, requirements="fastapi==0.115.8\n", pyproject=None)

        # when
        with patch.object(freshness, "fetch_latest_version", return_value="0.120.0"):
            freshness.check_dependency_freshness(ctx)

        # then
        assert any("minor version(s) behind" in warning for warning in ctx.warnings)

    def test_silent_when_up_to_date(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, requirements="fastapi==0.115.8\n", pyproject=None)

        # when
        with patch.object(freshness, "fetch_latest_version", return_value="0.115.8"):
            freshness.check_dependency_freshness(ctx)

        # then
        assert ctx.warnings == []

    def test_network_failure_is_skipped(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, requirements="fastapi==0.115.8\n", pyproject=None)

        # when
        with patch.object(freshness, "fetch_latest_version", return_value=None):
            result = freshness.check_dependency_freshness(ctx)

        # then
        assert result is True
        assert ctx.warnings == []


class TestAppModuleResolution:
    """The uvicorn target is resolved from metadata before layout guessing."""

    def test_prefers_pyproject_metadata(self, tmp_path: Path) -> None:
        # given
        pyproject = (
            VALID_PYPROJECT
            + '\n[tool.fastapi-fastkit]\napp_module = "src.app.main:app"\n'
        )
        ctx = make_context(tmp_path, pyproject=pyproject)

        # when / then
        assert smoke_module.resolve_app_module(ctx) == "src.app.main:app"

    def test_falls_back_to_template_config(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        ctx.template_config = {"app_module": "src.main:app"}

        # when / then
        assert smoke_module.resolve_app_module(ctx) == "src.main:app"

    def test_appends_default_attribute(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        ctx.template_config = {"app_module": "src.main"}

        # when / then
        assert smoke_module.resolve_app_module(ctx) == "src.main:app"

    def test_falls_back_to_layout(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        src_dir = Path(ctx.temp_path("src"))
        src_dir.mkdir()
        (src_dir / "main.py").write_text("app = 1\n")

        # when / then
        assert smoke_module.resolve_app_module(ctx) == "src.main:app"

    def test_returns_none_when_unresolvable(self, tmp_path: Path) -> None:
        ctx = make_context(tmp_path)
        assert smoke_module.resolve_app_module(ctx) is None


class TestSmokeCheck:
    """The smoke test boots the app; the subprocess is mocked out here."""

    def _context(self, tmp_path: Path) -> InspectionContext:
        ctx = make_context(tmp_path)
        ctx.template_config = {"app_module": "src.main:app"}
        ctx.venv_path = str(tmp_path / "venv")
        bin_dir = Path(ctx.venv_path) / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "python").write_text("")
        return ctx

    def test_skipped_when_disabled(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, options=InspectionOptions(run_smoke_test=False))

        # when / then
        assert smoke_module.check_smoke_test(ctx) is True

    def test_fails_without_environment(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)

        # when / then
        assert smoke_module.check_smoke_test(ctx) is False
        assert any("virtual environment" in error for error in ctx.errors)

    def test_fails_when_app_module_unresolvable(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        ctx.template_config = None

        # when / then
        assert smoke_module.check_smoke_test(ctx) is False
        assert any("app module" in error for error in ctx.errors)

    def test_passes_when_docs_answers(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        process = MagicMock()
        process.poll.return_value = None
        statuses = {"docs": 200, "health": 200}

        # when
        with (
            patch.object(smoke_module.subprocess, "Popen", return_value=process),
            patch.object(
                smoke_module,
                "_probe",
                side_effect=lambda url, timeout=5: statuses[url.rsplit("/", 1)[-1]],
            ),
        ):
            result = smoke_module.check_smoke_test(ctx)

        # then
        assert result is True
        assert ctx.errors == []
        process.terminate.assert_called_once()

    def test_missing_health_endpoint_is_not_an_error(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        process = MagicMock()
        process.poll.return_value = None
        statuses = {"docs": 200, "health": 404}

        # when
        with (
            patch.object(smoke_module.subprocess, "Popen", return_value=process),
            patch.object(
                smoke_module,
                "_probe",
                side_effect=lambda url, timeout=5: statuses[url.rsplit("/", 1)[-1]],
            ),
        ):
            result = smoke_module.check_smoke_test(ctx)

        # then
        assert result is True
        assert ctx.errors == []

    def test_broken_health_endpoint_fails(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        process = MagicMock()
        process.poll.return_value = None
        statuses = {"docs": 200, "health": 500}

        # when
        with (
            patch.object(smoke_module.subprocess, "Popen", return_value=process),
            patch.object(
                smoke_module,
                "_probe",
                side_effect=lambda url, timeout=5: statuses[url.rsplit("/", 1)[-1]],
            ),
        ):
            result = smoke_module.check_smoke_test(ctx)

        # then
        assert result is False
        assert any("/health returned HTTP 500" in error for error in ctx.errors)

    def test_server_crash_is_reported(self, tmp_path: Path) -> None:
        # given: the server process dies immediately
        ctx = self._context(tmp_path)
        process = MagicMock()
        process.poll.return_value = 1
        process.stdout.read.return_value = "ImportError: no module named src"

        # when
        with (
            patch.object(smoke_module.subprocess, "Popen", return_value=process),
            patch.object(smoke_module, "_probe", return_value=None),
        ):
            result = smoke_module.check_smoke_test(ctx)

        # then
        assert result is False
        assert any("exited before becoming reachable" in e for e in ctx.errors)

    def test_timeout_terminates_the_server(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        ctx.options.smoke_timeout = 0
        process = MagicMock()
        process.poll.return_value = None

        # when
        with (
            patch.object(smoke_module.subprocess, "Popen", return_value=process),
            patch.object(smoke_module, "_probe", return_value=None),
        ):
            result = smoke_module.check_smoke_test(ctx)

        # then
        assert result is False
        process.terminate.assert_called_once()


class TestFreeportAndProbeHelpers:
    """Small helpers used by the smoke test."""

    def test_find_free_port_returns_bindable_port(self) -> None:
        port = smoke_module.find_free_port()
        assert 1024 < port < 65536

    def test_probe_returns_status_for_http_error(self) -> None:
        # given
        import urllib.error

        error = urllib.error.HTTPError(
            url="http://x/health", code=404, msg="nf", hdrs=None, fp=None  # type: ignore[arg-type]
        )

        # when
        with patch("urllib.request.urlopen", side_effect=error):
            status = smoke_module._probe("http://x/health")

        # then
        assert status == 404

    def test_probe_returns_none_when_unreachable(self) -> None:
        # given
        import urllib.error

        # when
        with patch(
            "urllib.request.urlopen", side_effect=urllib.error.URLError("refused")
        ):
            status = smoke_module._probe("http://x/docs")

        # then
        assert status is None


class TestPyprojectHelpers:
    """Metadata parsing helpers shared by several checks."""

    def test_extract_dependency_names(self, tmp_path: Path) -> None:
        # given
        pyproject = tmp_path / "pyproject.toml-tpl"
        pyproject.write_text(VALID_PYPROJECT)

        # when
        names, error = checks.extract_pyproject_dependency_names(pyproject)

        # then
        assert error is None
        assert names == {"fastapi", "uvicorn"}

    def test_extract_reports_malformed_file(self, tmp_path: Path) -> None:
        # given
        pyproject = tmp_path / "pyproject.toml-tpl"
        pyproject.write_text("this is not = = toml")

        # when
        names, error = checks.extract_pyproject_dependency_names(pyproject)

        # then
        assert names == set()
        assert error is not None and "Invalid pyproject.toml-tpl" in error

    def test_parse_requirements_names_skips_comments(self, tmp_path: Path) -> None:
        # given
        requirements = tmp_path / "requirements.txt-tpl"
        requirements.write_text("# comment\nfastapi==1.0\n\nUvicorn>=0.1\n")

        # when
        names = checks.parse_requirements_names(requirements)

        # then
        assert names == {"fastapi", "uvicorn"}


class TestContextHelpers:
    """InspectionContext bookkeeping."""

    def test_add_error_and_warning(self, tmp_path: Path) -> None:
        ctx = make_context(tmp_path)
        ctx.add_error("boom")
        ctx.add_warning("careful")
        assert ctx.errors == ["boom"]
        assert ctx.warnings == ["careful"]

    def test_python_executable_requires_venv(self, tmp_path: Path) -> None:
        ctx = make_context(tmp_path)
        assert ctx.python_executable() is None
        ctx.venv_path = "/tmp/venv"
        assert ctx.python_executable() == "/tmp/venv/bin/python"

    def test_options_defaults(self) -> None:
        options: Dict[str, Any] = vars(InspectionOptions())
        assert options["offline"] is False
        assert options["run_smoke_test"] is True
        assert options["run_mypy"] is False
