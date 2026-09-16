from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from ts_tune import TuneParseError, parse


SAMPLE_TUNE = """<?xml version="1.0" encoding="UTF-8"?>
<msq>
  <constants>
    <setting name="reqFuel">6.2</setting>
  </constants>
  <table id="veTable1" rows="2" cols="2" />
</msq>
"""


def test_parse_from_text() -> None:
    tune = parse(SAMPLE_TUNE)

    assert tune.root.tag == "msq"
    constants = tune.root.find("constants")
    assert constants is not None
    setting = constants.find("setting")
    assert setting is not None
    assert setting.attributes["name"] == "reqFuel"
    assert setting.text == "6.2"


def test_parse_from_file() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "sample.msq"
        path.write_bytes(SAMPLE_TUNE.encode("utf-8"))
        resolved_path = str(path.resolve())

        tune = parse(path)

    assert tune.source == resolved_path
    table = tune.root.find("table")
    assert table is not None
    assert table.attributes["cols"] == "2"
    assert tune.to_dict()["source"] == resolved_path


def test_parse_raises_for_invalid_xml() -> None:
    with pytest.raises(TuneParseError):
        parse("<msq>")


def test_parse_raises_for_missing_file() -> None:
    with TemporaryDirectory() as directory:
        missing_path = Path(directory) / "missing-file.msq"

        with pytest.raises(FileNotFoundError) as exc_info:
            parse(str(missing_path))

        assert exc_info.value.filename == str(missing_path.resolve())
        assert "TunerStudio tune file not found" in str(exc_info.value)


def test_parse_raises_for_missing_file_pathlike() -> None:
    with TemporaryDirectory() as directory:
        missing_path = Path(directory) / "missing-file.msq"

        with pytest.raises(FileNotFoundError):
            parse(missing_path)


def test_parse_raises_for_directory() -> None:
    with TemporaryDirectory() as directory:
        with pytest.raises(IsADirectoryError):
            parse(directory)


def test_parse_raises_for_missing_absolute_unknown_extension_file() -> None:
    with TemporaryDirectory() as directory:
        missing_path = Path(directory) / "missing-file.custom"

        with pytest.raises(FileNotFoundError):
            parse(str(missing_path))


def test_parse_relative_unknown_extension_raises_parse_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(TuneParseError):
        parse("missing-file.custom")


def test_parse_raises_for_invalid_plain_text() -> None:
    with pytest.raises(TuneParseError):
        parse("not xml data")


def test_parse_raises_for_invalid_dotted_text() -> None:
    with pytest.raises(TuneParseError):
        parse("v1.0")


def test_parse_raises_for_unsupported_source_type() -> None:
    with pytest.raises(TypeError):
        parse(123)  # type: ignore[arg-type]


def test_parse_raises_for_bytes_input() -> None:
    with pytest.raises(TypeError):
        parse(SAMPLE_TUNE.encode("utf-8"))  # type: ignore[arg-type]
