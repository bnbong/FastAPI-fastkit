# --------------------------------------------------------------------------
# End-to-end coverage for the fastapi-domain-starter template + the
# pyproject-first contract introduced in v1.3.0.
#
# These tests are regression guards for issue #46: they fail fast when
# preset-specific generated output drifts (broken layout, missing
# identity markers, or a generated app that fails to import / serve).
#
# Scope on purpose stays narrow:
#   - run the inspector contract checks against the real shipped template
#     directory, no synthetic fixture;
#   - exercise the full ``fastkit startdemo fastapi-domain-starter`` flow
#     once and pin down what the generated artefact must contain;
#   - import the generated app inside its own ``.venv`` and verify
#     ``GET /api/v1/health`` actually responds 200.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Iterator

import pytest
from click.testing import CliRunner

from fastapi_fastkit.backend.inspector import TemplateInspector
from fastapi_fastkit.cli import fastkit_cli
from fastapi_fastkit.core.settings import FastkitConfig
from fastapi_fastkit.utils.main import is_fastkit_project

_TEMPLATE_NAME = "fastapi-domain-starter"


def _domain_starter_template_path() -> Path:
    """Return the absolute path to the shipped fastapi-domain-starter template."""
    settings = FastkitConfig()
    template_root = Path(settings.FASTKIT_TEMPLATE_ROOT)
    return template_root / _TEMPLATE_NAME


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def isolated_workspace(tmp_path: Path) -> Iterator[Path]:
    """Provide an isolated workspace + cwd for the duration of a test."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(original_cwd)


def _generate_domain_starter_project(
    runner: CliRunner,
    workspace: Path,
    project_name: str,
    description: str = "Domain starter E2E test",
) -> Path:
    """Run ``fastkit startdemo fastapi-domain-starter`` and return the project dir."""
    result = runner.invoke(
        fastkit_cli,
        ["startdemo", _TEMPLATE_NAME],
        input="\n".join(
            [
                project_name,
                "E2E Tester",
                "e2e@example.com",
                description,
                "uv",  # package manager
                "Y",  # proceed with creation
                "Y",  # create new project folder
            ]
        ),
    )
    assert result.exit_code == 0, f"startdemo exited non-zero. output:\n{result.output}"
    project_path = workspace / project_name
    assert (
        project_path.exists() and project_path.is_dir()
    ), f"Expected project directory not created. output:\n{result.output}"
    return project_path


# --------------------------------------------------------------------------
# 1. Contract-level: real shipping template still satisfies the
#    pyproject-first inspector contract.
# --------------------------------------------------------------------------


class TestRealTemplatePyprojectFirstContract:
    """Inspector contract checks against the real on-disk template.

    The synthetic fixtures in ``test_inspector.py`` exercise the contract
    code paths; this class is the production-side regression guard that
    pins ``fastapi-domain-starter``'s shipped layout to those same checks.
    """

    @pytest.fixture()
    def inspector(self, tmp_path: Path) -> TemplateInspector:
        # Skip the context manager (which copies the template to a temp
        # dir and installs deps) — the four contract checks only need the
        # static path to read files from.
        return TemplateInspector(
            str(_domain_starter_template_path()),
            temp_base_dir=str(tmp_path),
        )

    def test_file_structure_passes(self, inspector: TemplateInspector) -> None:
        assert inspector._check_file_structure() is True
        assert inspector.errors == []

    def test_file_extensions_pass(self, inspector: TemplateInspector) -> None:
        assert inspector._check_file_extensions() is True
        assert inspector.errors == []

    def test_dependencies_pass(self, inspector: TemplateInspector) -> None:
        assert inspector._check_dependencies() is True
        assert inspector.errors == []

    def test_template_ships_no_setup_py(self) -> None:
        """``fastapi-domain-starter`` is the canonical pyproject-only template.

        If a future change adds a ``setup.py-tpl`` here, the pyproject-first
        coverage story regresses — surface that loudly.
        """
        template_path = _domain_starter_template_path()
        assert (template_path / "pyproject.toml-tpl").exists()
        assert not (template_path / "setup.py-tpl").exists(), (
            "fastapi-domain-starter must remain pyproject-only; remove the "
            "setup.py-tpl shim or update this regression guard."
        )

    def test_template_pyproject_carries_identity_markers(self) -> None:
        """The shipped pyproject-tpl must declare both identity markers.

        Generated projects inherit them via metadata injection, but they
        have to start in the template — otherwise ``is_fastkit_project()``
        cannot tell a generated project apart from an unrelated FastAPI
        project before the user runs anything.
        """
        pyproject_tpl = _domain_starter_template_path() / "pyproject.toml-tpl"
        text = pyproject_tpl.read_text()
        assert "[FastAPI-fastkit templated]" in text
        assert "[tool.fastapi-fastkit]" in text
        assert "managed = true" in text


# --------------------------------------------------------------------------
# 2. End-to-end ``startdemo`` flow: pyproject markers survive injection.
# --------------------------------------------------------------------------


class TestStartdemoGeneratedPyproject:
    """``fastkit startdemo fastapi-domain-starter`` must produce a project
    whose pyproject.toml carries the canonical FastAPI-fastkit identity
    markers (post placeholder substitution + post tool-section injection).
    """

    def test_generated_pyproject_is_marked_as_fastkit_managed(
        self, runner: CliRunner, isolated_workspace: Path
    ) -> None:
        project_name = "marker-check"

        project_path = _generate_domain_starter_project(
            runner, isolated_workspace, project_name
        )

        pyproject = project_path / "pyproject.toml"
        assert pyproject.exists(), "generated project missing pyproject.toml"

        data = tomllib.loads(pyproject.read_text())

        # Description marker survives placeholder substitution.
        description = data["project"]["description"]
        assert (
            "[FastAPI-fastkit templated]" in description
        ), f"description missing identity marker; got: {description!r}"

        # Tool section carries the machine-readable marker.
        tool_section = data.get("tool", {}).get("fastapi-fastkit", {})
        assert (
            tool_section.get("managed") is True
        ), f"[tool.fastapi-fastkit].managed must be True; got: {tool_section!r}"

        # The detection helper must agree.
        assert is_fastkit_project(str(project_path)) is True


# --------------------------------------------------------------------------
# 3. End-to-end ``startdemo`` flow: generated app imports + ``/health`` 200.
# --------------------------------------------------------------------------


class TestStartdemoGeneratedAppRuns:
    """Full E2E: generate a project, then use its own venv to verify the
    FastAPI app actually imports cleanly and serves the health endpoint.

    This is the only test in the suite that exercises the generated
    ``src/app/main.py`` against a live ``TestClient`` — everything else
    only checks for file existence / content. Without this, regressions
    that produce syntactically-valid but functionally-broken main.py
    files (e.g. wrong import paths after a refactor) would slip through.
    """

    @pytest.mark.skipif(
        sys.platform == "win32",
        reason="venv binary path differs on Windows; the rest of the "
        "domain-starter flow is already covered there by other tests.",
    )
    def test_generated_app_serves_health_endpoint(
        self, runner: CliRunner, isolated_workspace: Path
    ) -> None:
        project_name = "health-check-e2e"
        project_path = _generate_domain_starter_project(
            runner, isolated_workspace, project_name
        )

        # The startdemo flow uses uv to provision a venv with the
        # template's deps installed. That's what we want to drive the
        # TestClient with — fastapi/httpx are not installed in the dev
        # environment that runs this test suite.
        venv_python = project_path / ".venv" / "bin" / "python"
        assert venv_python.exists(), (
            f"Generated venv python missing at {venv_python}. "
            f"startdemo did not provision a uv venv."
        )

        # Tiny driver script: import the app, hit /api/v1/health, write
        # status code + body to stdout. Keep this to one process so we
        # don't have to bring up an HTTP server.
        driver = (
            "import sys\n"
            "from fastapi.testclient import TestClient\n"
            "from src.app.main import app\n"
            "from src.app.core.config import settings\n"
            "client = TestClient(app)\n"
            "r = client.get(f'{settings.API_V1_PREFIX}/health')\n"
            "sys.stdout.write(f'{r.status_code}|{r.text}')\n"
        )

        completed = subprocess.run(
            [str(venv_python), "-c", driver],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert completed.returncode == 0, (
            f"Driver script failed.\nstdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

        status_str, _, body = completed.stdout.partition("|")
        assert (
            status_str == "200"
        ), f"/api/v1/health returned {status_str!r}; body: {body!r}"
        assert "ok" in body, f"/api/v1/health body must mention 'ok'; got: {body!r}"


# --------------------------------------------------------------------------
# 4. Smoke check: list-templates surfaces the new template.
# --------------------------------------------------------------------------


class TestDiscoverability:
    """``fastkit list-templates`` must show the domain-starter template
    with its descriptive title (not the raw <project_name> placeholder).
    """

    def test_list_templates_shows_domain_starter(
        self, runner: CliRunner, isolated_workspace: Path
    ) -> None:
        result = runner.invoke(fastkit_cli, ["list-templates"])

        assert result.exit_code == 0
        # Both the id and the descriptive heading must appear.
        assert (
            _TEMPLATE_NAME in result.output
        ), f"list-templates output missing '{_TEMPLATE_NAME}':\n{result.output}"
        assert "FastAPI Domain Starter" in result.output, (
            "list-templates must show the template's descriptive heading "
            "from README.md-tpl, not the <project_name> placeholder.\n"
            f"output:\n{result.output}"
        )
