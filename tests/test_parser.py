from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from py_ts_tune import TuneParseError, parse_tune, parse_tune_bytes, parse_tune_file


SAMPLE_TUNE = """<?xml version="1.0" encoding="UTF-8"?>
<msq>
  <constants>
    <setting name="reqFuel">6.2</setting>
  </constants>
  <table id="veTable1" rows="2" cols="2" />
</msq>
"""


class ParseTuneTests(unittest.TestCase):
    def test_parse_tune_from_text(self) -> None:
        tune = parse_tune(SAMPLE_TUNE)

        self.assertEqual(tune.root.tag, "msq")
        constants = tune.root.find("constants")
        self.assertIsNotNone(constants)
        setting = constants.find("setting")
        self.assertIsNotNone(setting)
        self.assertEqual(setting.attributes["name"], "reqFuel")
        self.assertEqual(setting.text, "6.2")

    def test_parse_tune_from_bytes(self) -> None:
        tune = parse_tune_bytes(SAMPLE_TUNE.encode("utf-8"))

        table = tune.root.find("table")
        self.assertIsNotNone(table)
        self.assertEqual(table.attributes["id"], "veTable1")
        self.assertEqual(table.attributes["rows"], "2")

    def test_parse_tune_from_file(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "sample.msq"
            path.write_bytes(SAMPLE_TUNE.encode("utf-8"))
            resolved_path = str(path.resolve())

            tune = parse_tune_file(path)

        self.assertEqual(tune.source, resolved_path)
        self.assertEqual(tune.root.find("table").attributes["cols"], "2")
        self.assertEqual(tune.to_dict()["source"], resolved_path)

    def test_parse_tune_raises_for_invalid_xml(self) -> None:
        with self.assertRaises(TuneParseError):
            parse_tune("<msq>")

    def test_parse_tune_raises_for_missing_file(self) -> None:
        with TemporaryDirectory() as directory:
            missing_path = Path(directory) / "missing-file.msq"

            with self.assertRaises(FileNotFoundError) as exc_info:
                parse_tune(str(missing_path))

            self.assertEqual(exc_info.exception.filename, str(missing_path.resolve()))
            self.assertIn("TunerStudio tune file not found", str(exc_info.exception))

    def test_parse_tune_file_raises_for_missing_file(self) -> None:
        with TemporaryDirectory() as directory:
            missing_path = Path(directory) / "missing-file.msq"

            with self.assertRaises(FileNotFoundError):
                parse_tune_file(missing_path)

    def test_parse_tune_raises_for_missing_unknown_extension_file(self) -> None:
        with TemporaryDirectory() as directory:
            missing_path = Path(directory) / "missing-file.custom"

            with self.assertRaises(FileNotFoundError):
                parse_tune(str(missing_path))

    def test_parse_tune_raises_for_invalid_plain_text(self) -> None:
        with self.assertRaises(TuneParseError):
            parse_tune("not xml data")


if __name__ == "__main__":
    unittest.main()
