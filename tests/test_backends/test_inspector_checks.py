# --------------------------------------------------------------------------
# Testcases for the individual template inspection checks.
#
# Each check is exercised against a synthetic template/generated-project pair
# built in a tmp_path, so the checks are validated independently of the
# TemplateInspector lifecycle.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import signal
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Tuple
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

    def test_mypy_passes_when_enabled_and_clean(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, options=InspectionOptions(run_mypy=True))
        completed = subprocess.CompletedProcess(
            args=["mypy"], returncode=0, stdout="Success: no issues found", stderr=""
        )

        # when
        with patch("subprocess.run", return_value=completed):
            result = lint.check_mypy(ctx)

        # then
        assert result is True

    def test_mypy_timeout_is_reported_as_error(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, options=InspectionOptions(run_mypy=True))

        # when
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="mypy", timeout=1),
        ):
            result = lint.check_mypy(ctx)

        # then
        assert result is False
        assert any("mypy timed out" in error for error in ctx.errors)

    def test_mypy_oserror_is_a_warning_not_a_failure(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path, options=InspectionOptions(run_mypy=True))

        # when
        with patch("subprocess.run", side_effect=OSError("mypy not found")):
            result = lint.check_mypy(ctx)

        # then
        assert result is True
        assert any("Could not run mypy" in warning for warning in ctx.warnings)

    def test_compileall_timeout_is_reported_as_error(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)

        # when
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="compileall", timeout=1),
        ):
            result = lint.check_compileall(ctx)

        # then
        assert result is False
        assert any("compileall timed out" in error for error in ctx.errors)

    def test_compileall_oserror_is_reported_as_error(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)

        # when
        with patch("subprocess.run", side_effect=OSError("no interpreter")):
            result = lint.check_compileall(ctx)

        # then
        assert result is False
        assert any("Failed to run compileall" in error for error in ctx.errors)


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

    def test_no_pins_found_returns_true(self, tmp_path: Path) -> None:
        # given - no requirements/pyproject dependency data to inspect
        ctx = make_context(tmp_path, requirements="# only comments\n", pyproject=None)

        # when
        with patch.object(freshness, "fetch_latest_version") as mock_fetch:
            result = freshness.check_dependency_freshness(ctx)

        # then
        assert result is True
        mock_fetch.assert_not_called()

    def test_unparsable_versions_are_skipped(self, tmp_path: Path) -> None:
        # given - pin/latest versions that don't match the major.minor regex
        ctx = make_context(tmp_path, requirements="fastapi==dev\n", pyproject=None)

        # when
        with patch.object(freshness, "fetch_latest_version", return_value="also-dev"):
            result = freshness.check_dependency_freshness(ctx)

        # then
        assert result is True
        assert ctx.warnings == []

    def test_pins_collected_from_pyproject_dependencies(self, tmp_path: Path) -> None:
        # given - only pyproject.toml-tpl carries a pinned dependency
        pyproject = '[project]\nname = "demo"\ndependencies = ["fastapi==0.115.8"]\n'
        ctx = make_context(tmp_path, requirements=None, pyproject=pyproject)

        # when
        with patch.object(freshness, "fetch_latest_version", return_value="1.0.0"):
            result = freshness.check_dependency_freshness(ctx)

        # then
        assert result is True
        assert any("major version(s) behind" in warning for warning in ctx.warnings)


class TestFetchLatestVersion:
    """``fetch_latest_version`` talks to PyPI and tolerates every failure mode."""

    def test_returns_version_on_success(self) -> None:
        # given
        response = MagicMock()
        response.__enter__.return_value = response
        response.__exit__.return_value = False
        response.read.return_value = b'{"info": {"version": "1.2.3"}}'

        # when
        with patch("urllib.request.urlopen", return_value=response):
            version = freshness.fetch_latest_version("fastapi")

        # then
        assert version == "1.2.3"

    def test_returns_none_when_version_missing(self) -> None:
        # given
        response = MagicMock()
        response.__enter__.return_value = response
        response.__exit__.return_value = False
        response.read.return_value = b'{"info": {}}'

        # when
        with patch("urllib.request.urlopen", return_value=response):
            version = freshness.fetch_latest_version("fastapi")

        # then
        assert version is None

    def test_returns_none_on_url_error(self) -> None:
        import urllib.error

        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("unreachable"),
        ):
            assert freshness.fetch_latest_version("fastapi") is None

    def test_returns_none_on_invalid_json(self) -> None:
        response = MagicMock()
        response.__enter__.return_value = response
        response.__exit__.return_value = False
        response.read.return_value = b"not json"

        with patch("urllib.request.urlopen", return_value=response):
            assert freshness.fetch_latest_version("fastapi") is None


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


#: Fake pid for the mocked server process. It must be a real int: the
#: production code refuses to signal a process group for anything else, and a
#: MagicMock pid used to collapse into pgid 1 and take down the CI runner.
FAKE_PID = 43210


@contextmanager
def no_real_signals(pid: int = FAKE_PID) -> Iterator[MagicMock]:
    """Neuter the process-group calls so no test can ever signal a real group."""
    with (
        patch.object(smoke_module.os, "getpgid", return_value=pid) as getpgid,
        patch.object(smoke_module.os, "killpg") as killpg,
    ):
        getpgid.side_effect = None
        yield killpg


class TestSignalGroup:
    """``_signal_group`` must never signal a group that is not ours."""

    def _process(self, pid: object) -> MagicMock:
        process = MagicMock()
        process.pid = pid
        return process

    def test_signals_own_group(self) -> None:
        # given
        process = self._process(FAKE_PID)

        # when
        with no_real_signals() as killpg:
            signalled = smoke_module._signal_group(process, signal.SIGTERM)

        # then
        assert signalled is True
        killpg.assert_called_once_with(FAKE_PID, signal.SIGTERM)

    def test_refuses_non_integer_pid(self) -> None:
        # given: an unconfigured mock, whose pid is a MagicMock
        process = MagicMock()

        # when
        with no_real_signals() as killpg:
            signalled = smoke_module._signal_group(process, signal.SIGTERM)

        # then
        assert signalled is False
        killpg.assert_not_called()

    @pytest.mark.parametrize("pid", [0, 1, -1])
    def test_refuses_reserved_pids(self, pid: int) -> None:
        # given / when
        with no_real_signals() as killpg:
            signalled = smoke_module._signal_group(self._process(pid), signal.SIGTERM)

        # then
        assert signalled is False
        killpg.assert_not_called()

    def test_refuses_when_process_is_not_group_leader(self) -> None:
        # given: the process shares someone else's group
        process = self._process(FAKE_PID)

        # when
        with (
            patch.object(smoke_module.os, "getpgid", return_value=FAKE_PID + 1),
            patch.object(smoke_module.os, "killpg") as killpg,
        ):
            signalled = smoke_module._signal_group(process, signal.SIGTERM)

        # then
        assert signalled is False
        killpg.assert_not_called()

    def test_refuses_the_current_process_group(self) -> None:
        # given: getpgid reports this interpreter's own group
        own_group = os.getpgrp()
        process = self._process(own_group)

        # when
        with (
            patch.object(smoke_module.os, "getpgid", return_value=own_group),
            patch.object(smoke_module.os, "killpg") as killpg,
        ):
            signalled = smoke_module._signal_group(process, signal.SIGTERM)

        # then
        assert signalled is False
        killpg.assert_not_called()

    def test_falls_back_when_getpgid_fails(self) -> None:
        # given
        process = self._process(FAKE_PID)

        # when
        with (
            patch.object(
                smoke_module.os, "getpgid", side_effect=ProcessLookupError("gone")
            ),
            patch.object(smoke_module.os, "killpg") as killpg,
        ):
            signalled = smoke_module._signal_group(process, signal.SIGTERM)

        # then
        assert signalled is False
        killpg.assert_not_called()


class TestSmokeCheck:
    """The smoke test boots the app; the subprocess is mocked out here."""

    def _process(self) -> MagicMock:
        """A mock server process with a realistic integer pid."""
        process = MagicMock()
        process.pid = FAKE_PID
        process.poll.return_value = None
        return process

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
        process = self._process()
        statuses = {"docs": 200, "health": 200}

        # when
        with (
            no_real_signals() as killpg,
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
        # The server's own group is signalled, not this process's.
        killpg.assert_called_once_with(FAKE_PID, signal.SIGTERM)
        process.terminate.assert_not_called()

    def test_missing_health_endpoint_is_not_an_error(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)
        process = self._process()
        statuses = {"docs": 200, "health": 404}

        # when
        with (
            no_real_signals() as killpg,
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
        process = self._process()
        statuses = {"docs": 200, "health": 500}

        # when
        with (
            no_real_signals() as killpg,
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
        process = self._process()
        process.poll.return_value = 1
        process.stdout.read.return_value = "ImportError: no module named src"

        # when
        with (
            no_real_signals() as killpg,
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
        process = self._process()

        # when
        with (
            no_real_signals() as killpg,
            patch.object(smoke_module.subprocess, "Popen", return_value=process),
            patch.object(smoke_module, "_probe", return_value=None),
        ):
            result = smoke_module.check_smoke_test(ctx)

        # then
        assert result is False
        killpg.assert_called_once_with(FAKE_PID, signal.SIGTERM)
        process.terminate.assert_not_called()


class TestAppModulePyprojectHelper:
    """``_app_module_from_pyproject`` handles a malformed generated file."""

    def test_returns_none_on_malformed_pyproject(self, tmp_path: Path) -> None:
        # given
        ctx = make_context(tmp_path)
        pyproject_path = Path(ctx.temp_path("pyproject.toml"))
        pyproject_path.write_text("not valid toml [[[")

        # when
        result = smoke_module._app_module_from_pyproject(ctx)

        # then
        assert result is None


class TestWaitForServer:
    """``_wait_for_server`` polls /docs until reachable, dead, or timed out."""

    def _process(self, poll_result: Optional[int] = None) -> MagicMock:
        process = MagicMock()
        process.poll.return_value = poll_result
        return process

    def test_returns_true_when_docs_answers_200(self) -> None:
        # given
        process = self._process()

        # when
        with patch.object(smoke_module, "_probe", return_value=200):
            reachable, reason = smoke_module._wait_for_server(
                process, "http://127.0.0.1:1", timeout=5
            )

        # then
        assert reachable is True
        assert reason == ""

    def test_returns_false_when_docs_answers_non_200(self) -> None:
        # given
        process = self._process()

        # when
        with patch.object(smoke_module, "_probe", return_value=500):
            reachable, reason = smoke_module._wait_for_server(
                process, "http://127.0.0.1:1", timeout=5
            )

        # then
        assert reachable is False
        assert "HTTP 500" in reason

    def test_times_out_when_never_reachable(self) -> None:
        # given
        process = self._process()

        # when
        with (
            patch.object(smoke_module, "_probe", return_value=None),
            patch.object(smoke_module.time, "sleep"),
        ):
            reachable, reason = smoke_module._wait_for_server(
                process, "http://127.0.0.1:1", timeout=0
            )

        # then
        assert reachable is False
        assert "did not become reachable" in reason


class TestTerminateEscalation:
    """``_terminate`` escalates from SIGTERM to SIGKILL when the server hangs."""

    def test_returns_immediately_when_already_exited(self) -> None:
        # given
        process = MagicMock()
        process.poll.return_value = 0

        # when
        smoke_module._terminate(process)

        # then
        process.terminate.assert_not_called()
        process.wait.assert_not_called()

    def test_escalates_to_sigkill_when_sigterm_does_not_stop_it(self) -> None:
        # given: the process never dies (poll always None, wait always times out)
        process = MagicMock()
        process.pid = FAKE_PID
        process.poll.return_value = None
        process.wait.side_effect = subprocess.TimeoutExpired(cmd="uvicorn", timeout=1)

        # when
        with no_real_signals() as killpg:
            smoke_module._terminate(process)

        # then
        assert killpg.call_args_list == [
            ((FAKE_PID, signal.SIGTERM),),
            ((FAKE_PID, signal.SIGKILL),),
        ]
        assert process.wait.call_count == 2

    def test_falls_back_to_process_kill_when_group_signal_unavailable(self) -> None:
        # given: no process group available, so it falls back to process.kill()
        process = MagicMock()
        process.pid = FAKE_PID
        process.poll.return_value = None
        process.wait.side_effect = subprocess.TimeoutExpired(cmd="uvicorn", timeout=1)

        # when
        with patch.object(
            smoke_module.os, "getpgid", side_effect=ProcessLookupError("gone")
        ):
            smoke_module._terminate(process)

        # then
        process.terminate.assert_called_once()
        process.kill.assert_called_once()


class TestSmokeCheckPortConflictAndStartupErrors:
    """The retry / error paths of ``check_smoke_test`` around Popen and ports."""

    def _process(self) -> MagicMock:
        process = MagicMock()
        process.pid = FAKE_PID
        process.poll.return_value = None
        return process

    def _context(self, tmp_path: Path) -> InspectionContext:
        ctx = make_context(tmp_path)
        ctx.template_config = {"app_module": "src.main:app"}
        ctx.venv_path = str(tmp_path / "venv")
        bin_dir = Path(ctx.venv_path) / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "python").write_text("")
        return ctx

    def test_popen_oserror_is_reported(self, tmp_path: Path) -> None:
        # given
        ctx = self._context(tmp_path)

        # when
        with patch.object(
            smoke_module.subprocess, "Popen", side_effect=OSError("no such file")
        ):
            result = smoke_module.check_smoke_test(ctx)

        # then
        assert result is False
        assert any("Failed to start the application server" in e for e in ctx.errors)

    def test_retries_on_port_conflict_then_succeeds(self, tmp_path: Path) -> None:
        # given: the first attempt reports a port bind conflict in its log
        ctx = self._context(tmp_path)
        process = self._process()
        calls = {"n": 0}

        def fake_wait_for_server(
            process: Any, base_url: str, timeout: int
        ) -> Tuple[bool, str]:
            calls["n"] += 1
            if calls["n"] == 1:
                return False, "server did not become reachable within 5s"
            return True, ""

        # when
        with (
            no_real_signals(),
            patch.object(smoke_module.subprocess, "Popen", return_value=process),
            patch.object(
                smoke_module, "_wait_for_server", side_effect=fake_wait_for_server
            ),
            patch.object(
                smoke_module,
                "_read_log_tail",
                return_value="ERROR: [Errno 98] Address already in use",
            ),
            patch.object(smoke_module, "_probe", return_value=200),
        ):
            result = smoke_module.check_smoke_test(ctx)

        # then
        assert result is True
        assert calls["n"] == 2

    def test_gives_up_after_exhausting_port_attempts(self, tmp_path: Path) -> None:
        # given: every attempt reports a port conflict
        ctx = self._context(tmp_path)
        process = self._process()

        # when
        with (
            no_real_signals(),
            patch.object(smoke_module.subprocess, "Popen", return_value=process),
            patch.object(
                smoke_module,
                "_wait_for_server",
                return_value=(False, "server did not become reachable within 5s"),
            ),
            patch.object(
                smoke_module,
                "_read_log_tail",
                return_value="ERROR: address already in use",
            ),
        ):
            result = smoke_module.check_smoke_test(ctx)

        # then
        assert result is False
        assert any("Smoke test failed" in e for e in ctx.errors)

    def test_health_endpoint_unreachable_is_a_warning(self, tmp_path: Path) -> None:
        # given: /docs is reachable but /health never answers
        ctx = self._context(tmp_path)
        process = self._process()

        # when
        with (
            no_real_signals(),
            patch.object(smoke_module.subprocess, "Popen", return_value=process),
            patch.object(smoke_module, "_wait_for_server", return_value=(True, "")),
            patch.object(smoke_module, "_probe", return_value=None),
        ):
            result = smoke_module.check_smoke_test(ctx)

        # then
        assert result is True
        assert any("/health did not respond" in w for w in ctx.warnings)


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
