# --------------------------------------------------------------------------
# Testcases of Rich library operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import os
import sys
from io import StringIO

from click.testing import CliRunner


class TestCLI:
    def setup_method(self) -> None:
        self.runner = CliRunner()
        self.current_workspace = os.getcwd()
        self.stdout = StringIO()
        self.old_stdout = sys.stdout
        sys.stdout = self.stdout

    def teardown_method(self, console) -> None:
        os.chdir(self.current_workspace)
        sys.stdout = self.old_stdout

    def test_success_message(self, console) -> None:
        # given
        from src.fastapi_fastkit.utils.main import print_success

        test_message = "this is success test"

        # when
        print_success(message=test_message, console=console)
        output = console.file.getvalue()

        # then
        assert "Success" in output and test_message in output

    def test_error_message(self, console) -> None:
        # given
        from src.fastapi_fastkit.utils.main import print_error

        test_message = "this is error test"

        # when
        print_error(message=test_message, console=console)
        output = console.file.getvalue()

        # then
        assert "Error" in output and test_message in output

    def test_warning_message(self, console) -> None:
        # given
        from src.fastapi_fastkit.utils.main import print_warning

        test_message = "this is warning test"

        # when
        print_warning(message=test_message, console=console)
        output = console.file.getvalue()

        # then
        assert "Warning" in output and test_message in output

    def test_info_message(self, console) -> None:
        # given
        from src.fastapi_fastkit.utils.main import print_info

        test_message = "this is info test"

        # when
        print_info(message=test_message, console=console)
        output = console.file.getvalue()

        # then
        assert "Info" in output and test_message in output
