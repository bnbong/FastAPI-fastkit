# --------------------------------------------------------------------------
# Testcases of base CLI operations.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from click.testing import CliRunner

from fastapi_fastkit.cli import fastkit_cli


class TestCLI:
    def setup_method(self) -> None:
        self.runner = CliRunner()

    def teardown_method(self) -> None:
        pass

    def test_echo(self, console) -> None:
        result = self.runner.invoke(fastkit_cli, ["echo"], terminal_width=80)  # type: ignore

        print(result.output)
        assert (
            "╭─────────────────────────── About FastAPI-fastkit ────────────────────────────╮"
            in result.output
        )
        assert (
            "│     ⚡️ FastAPI fastkit - fastest FastAPI initializer. ⚡️"
            in result.output
        )
        assert (
            "│     Deploy FastAPI app foundation instantly at your local!"
            in result.output
        )
        assert "│     - Project Maintainer : bnbong(JunHyeok Lee)" in result.output
        assert (
            "│     - Github : https://github.com/bnbong/FastAPI-fastkit"
            in result.output
        )
