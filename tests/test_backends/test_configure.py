# --------------------------------------------------------------------------
# Testcases of fastkit backends.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
from pathlib import Path

from click.testing import CliRunner

from fastapi_fastkit.cli import fastkit_cli


class TestBackend:
    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()

    def teardown_method(self) -> None:
        os.chdir(self.current_workspace)

    def test_project_root_and_user_workspace(self, temp_dir: str) -> None:
        """
        Test that USER_WORKSPACE can change dynamically and is independent
        of FASTKIT_PROJECT_ROOT, which should always point to the source directory.
        """
        # given
        os.chdir(temp_dir)

        # when
        result = self.runner.invoke(fastkit_cli, ["--debug", "echo"])

        # then
        expected_current_user_workspace = temp_dir
        expected_project_root = str(Path(__file__).parent.parent.parent)

        assert "running at debugging mode!!" in result.output
        assert expected_current_user_workspace in result.output
        assert expected_project_root in result.output
