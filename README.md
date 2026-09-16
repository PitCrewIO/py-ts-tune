# py-ts-tune

Python module for parsing EFI Analytics TunerStudio tune files.

`py_ts_tune` accepts:

- XML tune text already loaded in memory
- XML tune bytes that were read in binary mode
- a file path, which the library opens in binary mode and parses

The parser returns a small object model that preserves the XML structure without
requiring a hard-coded schema.

## Example

```python
from py_ts_tune import parse_tune

tune = parse_tune("example.msq")
print(tune.root.tag)

table = tune.root.find("table")
print(table.attributes)
```
