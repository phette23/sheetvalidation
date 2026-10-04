# https://docs.pola.rs/user-guide/lazy/schemas/
from pathlib import Path
from typing import TypedDict

import polars as pl


class SheetValidationError(TypedDict):
    original_file: str
    edited_file: str
    original_column_type: str
    edited_column_type: str
    message: str


def validate(
    original_file: Path, edited_files: list[Path]
) -> list[SheetValidationError]:
    return []
