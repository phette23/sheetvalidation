from pathlib import Path
from typing import Any

import fastexcel
import polars as pl
import pytest

from sheetvalidation.lib import (
    SheetValidationError,
    data_to_schema,
    read_csv_or_excel,
    validate_file,
)


@pytest.mark.parametrize(
    ("suffix", "contents", "expected"),
    [
        (
            ".csv",
            "id,name\n1,Ada\n2,Grace\n",
            pl.DataFrame({"id": [1, 2], "name": ["Ada", "Grace"]}),
        ),
        (
            ".tsv",
            "id\tname\n1\tAda\n2\tGrace\n",
            pl.DataFrame({"id": [1, 2], "name": ["Ada", "Grace"]}),
        ),
    ],
)
def test_read_csv_or_excel_reads_delimited_files(
    tmp_path, suffix: str, contents: str, expected: pl.DataFrame
) -> None:
    file_path: Path = tmp_path / f"data{suffix}"
    file_path.write_text(contents, encoding="utf-8")

    result: pl.DataFrame = read_csv_or_excel(file_path)

    assert result.equals(expected)


@pytest.mark.parametrize("suffix", [".xls", ".xlsx"])
def test_read_csv_or_excel_raises_for_invalid_excel_files(
    tmp_path, suffix: str
) -> None:
    file_path: Path = tmp_path / f"data{suffix}"
    file_path.write_bytes(b"not an Excel file")

    # Raised error is actually from fastexcel
    with pytest.raises(fastexcel.CalamineError):
        read_csv_or_excel(file_path)


def test_read_csv_or_excel_raises_for_unsupported_extension(tmp_path) -> None:
    file_path: Path = tmp_path / "data.json"
    file_path.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="unable to guess file type"):
        read_csv_or_excel(file_path)


def test_read_csv_or_excel_raises_for_empty_file(tmp_path) -> None:
    file_path: Path = tmp_path / "empty.csv"
    file_path.touch()

    with pytest.raises(pl.exceptions.NoDataError, match="empty CSV"):
        read_csv_or_excel(file_path)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            pl.DataFrame({"id": [1], "name": ["Ada"], "active": [True]}),
            {"id": pl.Int64, "name": pl.String, "active": pl.Boolean},
        ),
        (
            pl.DataFrame(schema={"id": pl.Int64, "name": pl.String}),
            {"id": pl.Int64, "name": pl.String},
        ),
    ],
)
def test_data_to_schema(data: pl.DataFrame, expected: dict[str, pl.DataType]) -> None:
    assert data_to_schema(data) == expected


@pytest.mark.parametrize(
    ("contents", "expected_error"),
    [
        (
            "id,Age\n1,Lorde\n2,25\n",
            [
                {
                    "row": 1,
                    "original_column_type": "Int64",
                    "cell_type": "String",
                    "message": "Row 1, Column Age: expected Int64, got String",
                }
            ],
        ),
        (
            "id,Age,active\nx,30,true\n2,thirty,false\n",
            [
                {
                    "row": 1,
                    "original_column_type": "Int64",
                    "cell_type": "String",
                    "message": "Row 1, Column id: expected Int64, got String",
                },
                {
                    "row": 2,
                    "original_column_type": "Int64",
                    "cell_type": "String",
                    "message": "Row 2, Column Age: expected Int64, got String",
                },
            ],
        ),
        ("id,Age\n1,\n2,25\n", []),
        ("id,Age,notes\n1,25,new\n2,30,columns\n", []),
        (
            "id,Age\n1,25\n2,not-a-number\n",
            [
                {
                    "row": 2,
                    "original_column_type": "Int64",
                    "cell_type": "String",
                    "message": "Row 2, Column Age: expected Int64, got String",
                }
            ],
        ),
    ],
)
def test_validate_file_checks_cells_against_schema(
    tmp_path, contents: str, expected_error: list[dict[str, object]]
) -> None:
    edited_file: Path = tmp_path / "edited.csv"
    edited_file.write_text(contents, encoding="utf-8")
    schema: dict[str, pl.DataType] = data_to_schema(
        pl.DataFrame(
            schema={
                "id": pl.Int64,
                "Age": pl.Int64,
                "active": pl.Boolean,
            }
        )
    )

    errors: list[SheetValidationError] = validate_file(schema, edited_file)

    actual_errors: list[dict[str, Any]] = [
        {
            "row": error["row"],
            "original_column_type": error["original_column_type"],
            "cell_type": error["cell_type"],
            "message": error["message"],
        }
        for error in errors
    ]
    assert actual_errors == expected_error
