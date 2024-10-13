# --------------------------------------------------------------------------
# Testcases of fastkit backends.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import shutil

from pathlib import Path

from click.testing import CliRunner


class TestBackend:
    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()
        self.temp_dir = os.path.join(self.current_workspace, "temp_test_workspace")
        os.makedirs(self.temp_dir, exist_ok=True)

    def teardown_method(self) -> None:
        os.chdir(self.current_workspace)
        shutil.rmtree(self.temp_dir)

    def test_project_root_and_user_workspace(self) -> None:
        """
        Test that USER_WORKSPACE can change dynamically and is independent
        of FASTKIT_PROJECT_ROOT, which should always point to the source directory.
        """
        # given
        os.chdir(self.temp_dir)
        from fastapi_fastkit.cli import fastkit_cli

        # when
        result = self.runner.invoke(fastkit_cli, ["--debug", "echo"])  # type: ignore

        # then
        expected_current_user_workspace = self.temp_dir
        expected_project_root = str(Path(__file__).parent.parent.parent)

        assert "running at debugging mode!!" in result.output
        assert expected_current_user_workspace in result.output
        assert expected_project_root in result.output
