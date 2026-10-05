from pathlib import Path

import fastexcel
import polars as pl
import pytest

from sheetvalidation.lib import data_to_schema, read_csv_or_excel


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
            {"id": "Int64", "name": "String", "active": "Boolean"},
        ),
        (
            pl.DataFrame(schema={"id": pl.Int64, "name": pl.String}),
            {"id": "Int64", "name": "String"},
        ),
    ],
)
def test_data_to_schema(data: pl.DataFrame, expected: dict[str, str]) -> None:
    assert data_to_schema(data) == expected
