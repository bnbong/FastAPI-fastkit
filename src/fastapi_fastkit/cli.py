# TODO : make logic with click(cli operation) & rick(decorate console outputs and indicate manuals)
# --------------------------------------------------------------------------
# This Module defines main and core CLI operations for FastAPI-fastkit.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
import click


@click.command()
def main() -> None:
    click.echo("Hello World!")
