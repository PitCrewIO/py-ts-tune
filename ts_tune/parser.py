'''Parser for TunerStudio tune XML files.'''

from __future__ import annotations

from os import PathLike
from pathlib import Path
from xml.etree import ElementTree

from .dataclasses import Tune, TuneNode


PATH_SUFFIXES = {".bin", ".msq", ".msqpart", ".table", ".xml"}


class TuneParseError(ValueError):
    """Raised when TunerStudio tune data cannot be parsed as XML."""

def parse_tune(source: str | bytes | PathLike[str]) -> Tune:
    """Parse a TunerStudio tune from XML text, bytes, or a path-like source.

    Existing files are loaded first. For string input that is not XML, values
    that look path-like, such as strings with path separators or filename
    extensions, are treated as filenames and raise FileNotFoundError when the
    file does not exist.
    """
    if isinstance(source, bytes):
        return parse_tune_bytes(source)

    if isinstance(source, PathLike):
        return parse_tune_file(source)

    if not isinstance(source, str):
        raise TypeError("source must be XML text, XML bytes, or a filesystem path")

    path = Path(source)
    if path.exists():
        return parse_tune_file(path)

    if _looks_like_xml(source):
        return _parse_xml(source)

    if _looks_like_path(source):
        resolved_path = path.resolve(strict=False)
        raise FileNotFoundError(2, "TunerStudio tune file not found", str(resolved_path))

    return _parse_xml(source)


def parse_tune_file(path: str | PathLike[str]) -> Tune:
    """Read tune data from ``path`` and parse it as TunerStudio XML."""

    file_path = Path(path).resolve(strict=False)
    try:
        data = file_path.read_bytes()
    except FileNotFoundError as exc:
        raise FileNotFoundError(2, "TunerStudio tune file not found", str(file_path)) from exc

    return _parse_xml(data, source=str(file_path))


def parse_tune_bytes(data: bytes) -> Tune:
    """Parse a TunerStudio tune from raw bytes."""

    return _parse_xml(data)


def _looks_like_xml(source: str) -> bool:
    """Return whether a string appears to contain XML content."""

    stripped = source.lstrip("\ufeff \t\r\n")
    return stripped.startswith("<?xml") or stripped.startswith("<")


def _looks_like_path(source: str) -> bool:
    """Return whether a string should be treated as a likely filename."""

    path = Path(source)
    filename = path.name
    return (
        path.suffix.lower() in PATH_SUFFIXES
        or "/" in source
        or "\\" in source
        or ("." in filename and "<" not in source and ">" not in source and "\n" not in source)
    )


def _parse_xml(data: str | bytes, source: str | None = None) -> Tune:
    """Parse XML data into a :class:`Tune` object."""

    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as exc:
        message = f"Invalid TunerStudio tune XML: {exc}"
        if source:
            message = f"{message} ({source})"
        raise TuneParseError(message) from exc

    return Tune(root=_build_node(root), source=source)


def _build_node(element: ElementTree.Element) -> TuneNode:
    """Recursively convert an XML element tree into :class:`TuneNode` objects."""

    text = element.text.strip() if element.text and element.text.strip() else None
    return TuneNode(
        tag=element.tag,
        attributes=dict(element.attrib),
        text=text,
        children=tuple(_build_node(child) for child in element),
    )
