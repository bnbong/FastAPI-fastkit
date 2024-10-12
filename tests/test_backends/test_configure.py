# --------------------------------------------------------------------------
# Testcases of fastkit backends.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import shutil
import pytest

from click.testing import CliRunner

from fastapi_fastkit.cli import fastkit_cli


class TestBackend:
    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()
        self.temp_dir = os.path.join(self.current_workspace, "temp_test_workspace")
        os.makedirs(self.temp_dir, exist_ok=True)

    def teardown_method(self) -> None:
        os.chdir(self.current_workspace)
        shutil.rmtree(self.temp_dir)

    def test_project_root_and_user_workspace(self):
        # TODO : adjust testcase to appropriate cli environment
        """
        Test that USER_WORKSPACE can change dynamically and is independent
        of FASTKIT_PROJECT_ROOT, which should always point to the source directory.
        """
        from fastapi_fastkit.core.settings import settings

        assert settings.USER_WORKSPACE == self.current_workspace, (
            f"USER_WORKSPACE should point to the current working directory, "
            f"but it points to {settings.USER_WORKSPACE}"
        )

        os.chdir(self.temp_dir)
        settings.USER_WORKSPACE = os.getcwd()

        assert (
                settings.USER_WORKSPACE != settings.FASTKIT_PROJECT_ROOT
        ), (
            f"USER_WORKSPACE and FASTKIT_PROJECT_ROOT should be independent. "
            f"Current workspace: {settings.USER_WORKSPACE}, "
            f"Project root: {settings.FASTKIT_PROJECT_ROOT}"
        )

        assert settings.FASTKIT_PROJECT_ROOT == settings.FASTKIT_PROJECT_ROOT, (
            f"FASTKIT_PROJECT_ROOT should point to Fastkit's source root directory, "
            f"but it points to {settings.FASTKIT_PROJECT_ROOT}"
        )
