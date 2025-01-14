# --------------------------------------------------------------------------
# Testcases of Rich library operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os

from click.testing import CliRunner


class TestCLI:
    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()

    def teardown_method(self, console) -> None:
        os.chdir(self.current_workspace)

    def test_echo(self) -> None:
        # given
        from src.fastapi_fastkit.backend import print_success

        # when
        result = self.runner.invoke(print_success(message="this is test"))

        # then
        print(result)
