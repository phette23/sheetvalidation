from pathlib import Path
from typing import TypedDict

import polars as pl


class SheetValidationError(TypedDict):
    original_file: str
    edited_file: str
    original_column_type: str
    edited_column_type: str
    message: str
    row: int


def read_csv_or_excel(file_path: Path) -> pl.DataFrame:
    """Abstract over CSV or Excel input."""
    if file_path.suffix in [".csv", ".tsv"]:
        separator = "\t" if file_path.suffix == ".tsv" else ","
        return pl.DataFrame(
            pl.read_csv(file_path, separator=separator, raise_if_empty=True)
        )
    elif file_path.suffix in [".xls", ".xlsx"]:
        return pl.DataFrame(pl.read_excel(file_path, raise_if_empty=True))
    else:
        raise ValueError(
            f"{file_path.name}: unable to guess file type from extension. Expecting .csv, .tsv, .xls, or .xlsx"
        )


def data_to_schema(data: pl.DataFrame) -> dict[str, str]:
    schema: dict[str, str] = {}
    for column in data.columns:
        schema[column] = str(data[column].dtype)
    return schema


def validate(
    original_file: Path, edited_files: list[Path]
) -> list[SheetValidationError]:
    errors: list[SheetValidationError] = []
    schema: dict[str, str] = data_to_schema(read_csv_or_excel(original_file))
    print(schema)
    for edited_file in edited_files:
        pass
    return errors
