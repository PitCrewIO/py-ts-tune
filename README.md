# py-ts-tune

Python module for parsing EFI Analytics TunerStudio tune files.

`ts_tune` accepts:

- XML tune text already loaded in memory
- a file path, which the library opens in binary mode and parses

Use `parse(...)` as the single public entry point. It checks existing files
first, then XML-looking strings, then known
tune-file names such as `.msq` or `.msqpart`.

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
from ts_tune import parse

tune = parse("example.msq")
print(tune.root.tag)

table = tune.root.find("table")
if table is not None:
    print(table.attributes)
```

## Running tests

```bash
poetry run pytest
```
