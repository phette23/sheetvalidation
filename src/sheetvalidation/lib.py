from pathlib import Path
from typing import TypedDict

import polars as pl


class SheetValidationError(TypedDict):
    original_file: str | None
    edited_file: str
    original_column_type: str
    cell_type: str
    message: str
    row: int


def read_csv_or_excel(file_path: Path) -> pl.DataFrame:
    """Abstract over CSV, TSV, or Excel input."""
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


def data_to_schema(data: pl.DataFrame) -> dict[str, pl.DataType]:
    return dict(data.schema)


def _cell_matches_type(cell: object, expected_type: pl.DataType) -> bool:
    if cell is None:
        return True

    cell_type: pl.DataType = pl.Series([cell]).dtype
    if cell_type == expected_type:
        return True
    if cell_type != pl.String:
        return False

    converted_cell: pl.Series = pl.Series([cell], dtype=pl.String).cast(
        expected_type, strict=False
    )
    return converted_cell[0] is not None


def validate_file(
    schema: dict[str, pl.DataType],
    edited_file: Path,
    original_file_name: str | None = None,
) -> list[SheetValidationError]:
    """Validate a single file against the original schema."""
    errors: list[SheetValidationError] = []
    edited_data: pl.DataFrame = read_csv_or_excel(edited_file)

    for row_index, row in enumerate(edited_data.iter_rows()):
        for column, cell in zip(edited_data.columns, row):
            # TODO question about ignoring newly added columns
            if column not in schema:
                continue

            original_column_type: pl.DataType = schema[column]
            if not _cell_matches_type(cell, original_column_type):
                cell_type: str = str(pl.Series([cell]).dtype)
                errors.append(
                    SheetValidationError(
                        original_file=original_file_name,
                        edited_file=str(edited_file),
                        original_column_type=str(original_column_type),
                        cell_type=cell_type,
                        message=(
                            f"Row {row_index + 1}, Column {column}: expected "
                            f'{original_column_type}, got {cell_type} "{cell}"'
                        ),
                        # Index rows from 1, not 0
                        row=row_index + 1,
                    )
                )

    return errors


def validate(
    original_file: Path, edited_files: list[Path]
) -> list[SheetValidationError]:
    """Create a schema from the original file and validate each edited file against it."""
    errors: list[SheetValidationError] = []
    original_file_name: str = str(original_file)
    schema: dict[str, pl.DataType] = data_to_schema(read_csv_or_excel(original_file))
    for edited_file in edited_files:
        errors.extend(
            validate_file(schema, edited_file, original_file_name=original_file_name)
        )
    return errors
