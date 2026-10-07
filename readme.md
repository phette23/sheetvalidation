# Sheet Validation

Check a tabular data file against another one to see if they share the same structure. This is meant to be a quick check that's useful without needing to build a data dictionary or schema; you can take an existing metadata spreadsheet and compare it to a new one to see if their structures match (same columns with same data types). For instance, you can edit `authorities.csv` and compare it with the original `authorities.csv.bak` to see if the changes you made are valid.

## Example

Say we have a spreadsheet with an `Age` column and we accidentally change one of its values to be a string.

Original data:

| Name | Age |
| ----- | --- |
| Audre | 30 |
| Herman | 25 |

Edited data:

| Name | Age |
| ----- | --- |
| Audre | Lorde |
| Herman | 25 |

```sh
uv run sheetvalidation original.csv edited.csv
Row 1 Column Age: expected Int64, got String "Lorde"
```

The goal is for this tool to catch these types of errors.

## Setup

```sh
uv sync
```

## Usage

### Command Line

```sh
uv run sheetvalidation original.csv edited.csv
uv run sheetvalidation original.csv edited.csv edited2.csv edited3.csv
uv run sheetvalidation --ignore-columns=column1,column2 original.csv edited.csv
# TODO support an actual template file that specifies column data types rather than inferring them
uv run sheetvalidation --template template.csv data.csv
```

### Python API

```python
from sheetvalidation import validate

errors = validate("original.csv", ["edited.csv"])
for e in errors:
    # errors are dicts like
    # { "original_file": "original.csv", "edited_file": "edited.csv",
    # "original_column_type": "float", "edited_column_type": "str",
    # "message": "Columns have different data types" }
    print(e)
```

## Limitations

The more robust the original tabular data is, showing all the potential types in a given column, the more accurate the validation is. If you have a string column that happens to contain only integers in the original file, then the validation assumes that the column is supposed to be integers only and throws an error if the edited file has a string in that column.

## Dev

```sh
uv run pytest # tests
uv run ruff check src/ # linting
uv run ruff format src/ # formatting
```
