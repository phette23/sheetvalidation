from pathlib import Path

import click

from .lib import SheetValidationError, validate


@click.command()
@click.help_option("--help", "-h")
@click.argument(
    "files", nargs=-1, type=click.Path(dir_okay=False, exists=True, path_type=Path)
)
@click.option(
    "--ignore-columns",
    "-i",
    help="Columns to ignore during validation.",
    type=str,
)
def main(files: list[Path], ignore_columns: str) -> list[SheetValidationError]:
    """
    \b
    Validate tabular data structures match. Example:
    sheetvalidation original.csv edited.csv [edited2.csv ...]
    """
    if len(files) < 2:
        raise click.UsageError("At least two files must be provided for validation.")

    print(f"Validating {len(files) - 1} file(s) against {files[0]}...")
    errors: list[SheetValidationError] = validate(files[0], files[1:])
    # TODO better output
    for error in errors:
        print(error["message"])
    return errors
