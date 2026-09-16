# py-ts-tune

Python module for parsing EFI Analytics TunerStudio tune files.

`ts_tune` accepts:

- XML tune text already loaded in memory
- XML tune bytes that were read in binary mode
- a file path, which the library opens in binary mode and parses

Use `parse_tune(...)` as a convenience entry point, or call `parse_tune_file(...)`
and `parse_tune_bytes(...)` directly when you want to avoid any ambiguity. The
generic `parse_tune(...)` helper checks existing files first, then XML-looking
strings, then known tune-file names such as `.msq` or `.msqpart`.

The parser returns a small object model that preserves the XML structure without
requiring a hard-coded schema.

## Installation

```bash
poetry add py-ts-tune
```

```bash
pip install py-ts-tune
```

## Example

```python
from ts_tune import parse_tune

tune = parse_tune("example.msq")
print(tune.root.tag)

table = tune.root.find("table")
if table is not None:
    print(table.attributes)
```

## Running tests

```bash
poetry run pytest
```
