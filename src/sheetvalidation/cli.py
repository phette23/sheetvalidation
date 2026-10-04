from pathlib import Path

import click


@click.command()
@click.help_option("--help", "-h")
@click.argument("files", nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--ignore-columns",
    "-i",
    help="Columns to ignore during validation.",
    type=str,
)
def main(files: list[Path], ignore_columns: str) -> None:
    """
    \b
    Validate tabular data structures match. Example:
    sheetvalidation original.csv edited.csv [edited2.csv ...]
    """
    click.echo("Hello from sheetvalidation!")
