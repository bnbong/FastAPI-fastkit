# --------------------------------------------------------------------------
# Testcases for the CLI's error paths and less common branches: config-file
# problems, --save-config, list-templates edge cases, addroute/deleteproject
# rejection paths, and runserver's virtual-environment fallbacks.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from fastapi_fastkit.cli import fastkit_cli

MINIMAL_CONFIG: Dict[str, Any] = {
    "project_name": "config-driven",
    "author": "bnbong",
    "author_email": "bbbong9@gmail.com",
    "description": "created from a config file",
    "package_manager": "pip",
    "architecture_preset": "minimal",
    "database": {"type": "None", "packages": []},
    "authentication": "None",
    "async_tasks": "None",
    "caching": "None",
    "monitoring": "None",
    "testing": "None",
    "utilities": [],
    "all_dependencies": ["fastapi", "uvicorn"],
}


class TestCLIBase:
    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()

    def teardown_method(self) -> None:
        os.chdir(self.current_workspace)


class TestConfigLoadErrorPaths(TestCLIBase):
    """``--config`` error reporting for load / validation / schema failures."""

    def test_config_with_bad_extension_is_rejected(self, tmp_path: Path) -> None:
        # given
        config_path = tmp_path / "fastkit.config.ini"
        config_path.write_text("nope")
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(fastkit_cli, ["init", "--config", str(config_path)])

        # then
        assert "Unsupported config file extension" in result.output

    def test_config_with_malformed_axis_is_rejected(self, tmp_path: Path) -> None:
        # given: an axis value of the wrong shape is caught by schema
        # validation before generation ever starts
        config = dict(MINIMAL_CONFIG, caching=["Redis"])
        config_path = tmp_path / "fastkit.config.json"
        config_path.write_text(json.dumps(config))
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(fastkit_cli, ["init", "--config", str(config_path)])

        # then
        assert "takes a single choice, not a list" in result.output
        assert not (tmp_path / "config-driven").exists()


class TestSaveConfigOption(TestCLIBase):
    """``--save-config`` and the interactive save-prompt path."""

    def test_save_config_writes_selections_after_interactive_flow(
        self, tmp_path: Path
    ) -> None:
        # given
        os.chdir(tmp_path)
        save_path = tmp_path / "saved.config.json"

        # when: the interactive builder is stubbed so this test only exercises
        # the CLI's own save/scaffold wiring
        with patch("fastapi_fastkit.cli.InteractiveConfigBuilder") as mock_builder_cls:
            mock_builder_cls.return_value.run_interactive_flow.return_value = dict(
                MINIMAL_CONFIG
            )
            result = self.runner.invoke(
                fastkit_cli,
                [
                    "init",
                    "--interactive",
                    "--save-config",
                    str(save_path),
                    "--no-venv",
                ],
                input="Y\n",
            )

        # then
        assert save_path.exists(), result.output
        saved = json.loads(save_path.read_text())
        assert saved["project_name"] == "config-driven"

    def test_save_config_reports_unsupported_extension(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)
        save_path = tmp_path / "saved.config.ini"

        # when
        with patch("fastapi_fastkit.cli.InteractiveConfigBuilder") as mock_builder_cls:
            mock_builder_cls.return_value.run_interactive_flow.return_value = dict(
                MINIMAL_CONFIG
            )
            result = self.runner.invoke(
                fastkit_cli,
                [
                    "init",
                    "--interactive",
                    "--save-config",
                    str(save_path),
                    "--no-venv",
                ],
                input="Y\n",
            )

        # then
        assert "Could not save config file" in result.output

    def test_interactive_cancel_returns_without_scaffolding(
        self, tmp_path: Path
    ) -> None:
        # given
        os.chdir(tmp_path)

        # when
        with patch("fastapi_fastkit.cli.InteractiveConfigBuilder") as mock_builder_cls:
            mock_builder_cls.return_value.run_interactive_flow.return_value = None
            result = self.runner.invoke(fastkit_cli, ["init", "--interactive"])

        # then
        assert result.exit_code == 0
        assert os.listdir(tmp_path) == []

    def test_offer_config_save_prompts_when_stdin_is_a_tty_and_declined(
        self, tmp_path: Path
    ) -> None:
        """``_offer_config_save`` asks (and saves nothing) for an interactive tty."""
        # given
        from fastapi_fastkit.cli import _offer_config_save

        # when: a tty session that declines the save prompt
        with (
            patch("fastapi_fastkit.cli.sys.stdin.isatty", return_value=True),
            patch("fastapi_fastkit.cli.click.confirm", return_value=False) as confirm,
        ):
            _offer_config_save(dict(MINIMAL_CONFIG), None)

        # then
        confirm.assert_called_once()
        assert not any(tmp_path.glob("*.json"))

    def test_offer_config_save_prompts_for_a_path_when_confirmed(
        self, tmp_path: Path
    ) -> None:
        """Confirming the prompt asks for a path and saves the config there."""
        # given
        from fastapi_fastkit.cli import _offer_config_save

        save_path = tmp_path / "prompted.config.json"

        # when
        with (
            patch("fastapi_fastkit.cli.sys.stdin.isatty", return_value=True),
            patch("fastapi_fastkit.cli.click.confirm", return_value=True),
            patch("fastapi_fastkit.cli.click.prompt", return_value=str(save_path)),
        ):
            _offer_config_save(dict(MINIMAL_CONFIG), None)

        # then
        assert save_path.exists()


class TestListTemplatesEdgeCases(TestCLIBase):
    def test_missing_template_directory_is_reported(self, tmp_path: Path) -> None:
        # given: FastkitConfig() recomputes FASTKIT_TEMPLATE_ROOT on every
        # invocation, so the private resolver is patched instead of the class
        # attribute directly.
        missing = tmp_path / "does-not-exist"

        # when
        with patch(
            "fastapi_fastkit.core.settings.FastkitConfig._FastkitConfig__get_template_root",
            return_value=missing,
        ):
            result = self.runner.invoke(fastkit_cli, ["list-templates"])

        # then
        assert "Template directory not found" in result.output

    def test_empty_template_directory_reports_no_templates(
        self, tmp_path: Path
    ) -> None:
        # when
        with patch(
            "fastapi_fastkit.core.settings.FastkitConfig._FastkitConfig__get_template_root",
            return_value=tmp_path,
        ):
            result = self.runner.invoke(fastkit_cli, ["list-templates"])

        # then
        assert "No available templates" in result.output


class TestStartdemoRejectionPaths(TestCLIBase):
    def test_invalid_project_name_is_rejected(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(
            fastkit_cli,
            [
                "startdemo",
                "fastapi-default",
                "--project-name",
                "1bad-name",
                "--author",
                "bnbong",
                "--author-email",
                "bbbong9@gmail.com",
                "--description",
                "demo",
            ],
        )

        # then
        assert "Invalid project name" in result.output

    def test_existing_project_directory_is_rejected(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)
        (tmp_path / "existing-demo").mkdir()

        # when
        result = self.runner.invoke(
            fastkit_cli,
            [
                "startdemo",
                "fastapi-default",
                "--project-name",
                "existing-demo",
                "--author",
                "bnbong",
                "--author-email",
                "bbbong9@gmail.com",
                "--description",
                "demo",
            ],
        )

        # then
        assert "already exists" in result.output


class TestAddrouteRejectionPaths(TestCLIBase):
    def test_named_project_directory_missing_is_reported(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)

        # when
        result = self.runner.invoke(fastkit_cli, ["addroute", "user", "does-not-exist"])

        # then
        assert "does not exist" in result.output

    def test_named_project_not_a_fastkit_project_is_reported(
        self, tmp_path: Path
    ) -> None:
        # given
        os.chdir(tmp_path)
        (tmp_path / "plain-dir").mkdir()

        # when
        result = self.runner.invoke(fastkit_cli, ["addroute", "user", "plain-dir"])

        # then
        assert "is not a FastAPI-fastkit project" in result.output

    def test_non_identifier_route_name_is_rejected(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)
        (tmp_path / "proj" / "src").mkdir(parents=True)
        (tmp_path / "proj" / "setup.py").write_text(
            "from setuptools import setup\nsetup(description='Created with FastAPI-fastkit')\n"
        )

        # when
        result = self.runner.invoke(fastkit_cli, ["addroute", "1-bad", "proj"])

        # then
        assert "not a valid Python identifier" in result.output

    def test_keyword_route_name_is_rejected(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)
        (tmp_path / "proj" / "src").mkdir(parents=True)
        (tmp_path / "proj" / "setup.py").write_text(
            "from setuptools import setup\nsetup(description='Created with FastAPI-fastkit')\n"
        )

        # when
        result = self.runner.invoke(fastkit_cli, ["addroute", "class", "proj"])

        # then
        assert "Python keyword" in result.output

    def test_add_new_route_exception_is_reported(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)
        (tmp_path / "proj" / "src").mkdir(parents=True)
        (tmp_path / "proj" / "setup.py").write_text(
            "from setuptools import setup\nsetup(description='Created with FastAPI-fastkit')\n"
        )

        # when
        with patch(
            "fastapi_fastkit.cli.add_new_route", side_effect=RuntimeError("boom")
        ):
            result = self.runner.invoke(
                fastkit_cli, ["addroute", "user", "proj"], input="Y\n"
            )

        # then
        assert "Error during route addition" in result.output


class TestDeleteprojectRejectionPaths(TestCLIBase):
    def test_non_fastkit_project_is_rejected(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)
        (tmp_path / "plain-dir").mkdir()

        # when
        with patch(
            "fastapi_fastkit.core.settings.FastkitConfig.USER_WORKSPACE",
            str(tmp_path),
        ):
            result = self.runner.invoke(
                fastkit_cli, ["deleteproject", "plain-dir"], input="Y\n"
            )

        # then
        assert "is not a FastAPI-fastkit project" in result.output

    def test_rmtree_failure_is_reported(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)
        project_dir = tmp_path / "proj"
        project_dir.mkdir()
        (project_dir / "setup.py").write_text(
            "from setuptools import setup\nsetup(description='Created with FastAPI-fastkit')\n"
        )

        # when
        with (
            patch(
                "fastapi_fastkit.core.settings.FastkitConfig.USER_WORKSPACE",
                str(tmp_path),
            ),
            patch(
                "fastapi_fastkit.cli.shutil.rmtree",
                side_effect=OSError("permission denied"),
            ),
        ):
            result = self.runner.invoke(
                fastkit_cli, ["deleteproject", "proj"], input="Y\n"
            )

        # then
        assert "Error during project deletion" in result.output


class TestRunserverBranches(TestCLIBase):
    def test_missing_venv_declined_returns_without_running(
        self, tmp_path: Path
    ) -> None:
        # given
        os.chdir(tmp_path)

        # when
        with patch(
            "fastapi_fastkit.core.settings.FastkitConfig.USER_WORKSPACE",
            str(tmp_path),
        ):
            result = self.runner.invoke(fastkit_cli, ["runserver"], input="N\n")

        # then
        assert "Virtual environment not found" in result.output
        assert "Starting FastAPI server" not in result.output

    def test_missing_venv_accepted_falls_back_to_system_python(
        self, tmp_path: Path
    ) -> None:
        # given: no .venv, but a resolvable app module
        os.chdir(tmp_path)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("app = None\n")

        # when
        with (
            patch(
                "fastapi_fastkit.core.settings.FastkitConfig.USER_WORKSPACE",
                str(tmp_path),
            ),
            patch("fastapi_fastkit.cli.subprocess.run") as mock_run,
        ):
            result = self.runner.invoke(fastkit_cli, ["runserver"], input="Y\n")

        # then
        assert "Starting FastAPI server" in result.output
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0][0] == "uvicorn"

    def test_missing_interpreter_in_venv_declined_returns(self, tmp_path: Path) -> None:
        # given: a .venv directory exists, but has no python interpreter
        os.chdir(tmp_path)
        (tmp_path / ".venv" / "bin").mkdir(parents=True)

        # when
        with patch(
            "fastapi_fastkit.core.settings.FastkitConfig.USER_WORKSPACE",
            str(tmp_path),
        ):
            result = self.runner.invoke(fastkit_cli, ["runserver"], input="N\n")

        # then
        assert "Python interpreter not found" in result.output
        assert "Starting FastAPI server" not in result.output

    def test_app_module_unresolvable_is_reported(self, tmp_path: Path) -> None:
        # given: a valid venv but no main.py anywhere
        os.chdir(tmp_path)
        bin_dir = tmp_path / ".venv" / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "python").write_text("")

        # when
        with patch(
            "fastapi_fastkit.core.settings.FastkitConfig.USER_WORKSPACE",
            str(tmp_path),
        ):
            result = self.runner.invoke(fastkit_cli, ["runserver"])

        # then
        assert "Could not find 'main.py'" in result.output

    def test_runserver_uses_venv_python_and_extends_pythonpath(
        self, tmp_path: Path
    ) -> None:
        # given
        os.chdir(tmp_path)
        bin_dir = tmp_path / ".venv" / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "python").write_text("")
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("app = None\n")

        # when
        with (
            patch(
                "fastapi_fastkit.core.settings.FastkitConfig.USER_WORKSPACE",
                str(tmp_path),
            ),
            patch("fastapi_fastkit.cli.subprocess.run") as mock_run,
            patch.dict(os.environ, {"PYTHONPATH": "/already/here"}),
        ):
            result = self.runner.invoke(fastkit_cli, ["runserver"])

        # then
        assert "Using Python from virtual environment" in result.output
        assert mock_run.call_args[0][0][0] == str(bin_dir / "python")
        env = mock_run.call_args.kwargs["env"]
        assert env["PYTHONPATH"].endswith(":/already/here")

    def test_called_process_error_is_reported(self, tmp_path: Path) -> None:
        # given
        os.chdir(tmp_path)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("app = None\n")

        # when
        with (
            patch(
                "fastapi_fastkit.core.settings.FastkitConfig.USER_WORKSPACE",
                str(tmp_path),
            ),
            patch(
                "fastapi_fastkit.cli.subprocess.run",
                side_effect=subprocess.CalledProcessError(1, ["uvicorn"]),
            ),
        ):
            result = self.runner.invoke(fastkit_cli, ["runserver"], input="Y\n")

        # then
        assert "Failed to start FastAPI server" in result.output

    def test_file_not_found_with_venv_reports_uvicorn_missing_in_venv(
        self, tmp_path: Path
    ) -> None:
        # given
        os.chdir(tmp_path)
        bin_dir = tmp_path / ".venv" / "bin"
        bin_dir.mkdir(parents=True)
        (bin_dir / "python").write_text("")
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("app = None\n")

        # when
        with (
            patch(
                "fastapi_fastkit.core.settings.FastkitConfig.USER_WORKSPACE",
                str(tmp_path),
            ),
            patch(
                "fastapi_fastkit.cli.subprocess.run",
                side_effect=FileNotFoundError("no such file"),
            ),
        ):
            result = self.runner.invoke(fastkit_cli, ["runserver"])

        # then
        assert "Failed to run Python from the virtual environment" in result.output

    def test_file_not_found_without_venv_reports_uvicorn_missing_in_system(
        self, tmp_path: Path
    ) -> None:
        # given
        os.chdir(tmp_path)
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("app = None\n")

        # when
        with (
            patch(
                "fastapi_fastkit.core.settings.FastkitConfig.USER_WORKSPACE",
                str(tmp_path),
            ),
            patch(
                "fastapi_fastkit.cli.subprocess.run",
                side_effect=FileNotFoundError("no such file"),
            ),
        ):
            result = self.runner.invoke(fastkit_cli, ["runserver"], input="Y\n")

        # then
        assert "uvicorn not found" in result.output
