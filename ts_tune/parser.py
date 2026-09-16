'''Parser for TunerStudio tune XML files.'''

from __future__ import annotations

import errno
from os import PathLike, fspath
from pathlib import Path
from xml.etree import ElementTree

from .dataclasses import Tune, TuneNode, freeze_attributes


PATH_SUFFIXES = {".bin", ".msq", ".msqpart", ".table", ".xml"}


class TuneParseError(ValueError):
    """Raised when TunerStudio tune data cannot be parsed as XML."""


def parse(source: str | PathLike[str]) -> Tune:
    """Parse a TunerStudio tune from XML text or a path-like source.

    Existing files are loaded first. For string input that is not XML, values
    that look path-like, such as strings with path separators or known tune
    file extensions, are treated as filenames and raise FileNotFoundError when
    the file does not exist. Relative strings without path separators and with
    unknown extensions are treated as XML text and therefore raise
    TuneParseError when they are not valid XML. After the existing-file check,
    strings beginning with ``<`` are treated as XML text before any remaining
    filename heuristics are applied. File-related errors report the resolved
    filesystem path.
    """
    if isinstance(source, PathLike):
        return _parse_file(_coerce_path(source))

    if not isinstance(source, str):
        raise TypeError("source must be XML text or a filesystem path")

    path = Path(source)
    if path.exists():
        return _parse_file(path)

    if _looks_like_xml(source):
        return _parse_xml(source)

    if _looks_like_path(path, source):
        return _parse_file(path)

    return _parse_xml(source)


def _parse_file(path: str | PathLike[str]) -> Tune:
    """Read tune data from ``path`` in binary mode and parse it as XML."""

    file_path = _coerce_path(path).resolve(strict=False)
    if file_path.is_dir():
        raise IsADirectoryError(errno.EISDIR, "TunerStudio tune path is a directory", str(file_path))

    try:
        with file_path.open("rb") as file_obj:
            root = ElementTree.parse(file_obj).getroot()
    except FileNotFoundError as exc:
        raise FileNotFoundError(2, "TunerStudio tune file not found", str(file_path)) from exc
    except ElementTree.ParseError as exc:
        message = f"Invalid TunerStudio tune XML: {exc} ({file_path})"
        raise TuneParseError(message) from exc

    return Tune(root=_build_node(root), source=str(file_path))


def _looks_like_xml(source: str) -> bool:
    """Return whether a string appears to contain XML content."""

    stripped = source.lstrip("\ufeff \t\r\n")
    return stripped.startswith("<")


def _looks_like_path(path: Path, source: str) -> bool:
    """Return whether a string should be treated as a likely filename."""

    return path.is_absolute() or path.suffix.lower() in PATH_SUFFIXES or "/" in source or "\\" in source


def _coerce_path(path: str | PathLike[str]) -> Path:
    """Convert a path-like input to ``Path`` while rejecting byte paths."""

    raw_path = fspath(path)
    if not isinstance(raw_path, str):
        raise TypeError("source must be XML text or a string filesystem path")
    return Path(raw_path)


def _parse_xml(data: str) -> Tune:
    """Parse XML data into a :class:`Tune` object."""

    try:
        root = ElementTree.fromstring(data.lstrip("\ufeff \t\r\n"))
    except ElementTree.ParseError as exc:
        message = f"Invalid TunerStudio tune XML: {exc}"
        raise TuneParseError(message) from exc

    return Tune(root=_build_node(root))


def _build_node(element: ElementTree.Element) -> TuneNode:
    """Recursively convert an XML element tree into :class:`TuneNode` objects."""

    text = element.text.strip() if element.text and element.text.strip() else None
    return TuneNode(
        tag=element.tag,
        attributes=freeze_attributes(dict(element.attrib)),
        text=text,
        children=tuple(_build_node(child) for child in element),
    )
