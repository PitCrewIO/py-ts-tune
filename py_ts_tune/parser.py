from __future__ import annotations

from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


PATH_SUFFIXES = {".bin", ".msq", ".msqpart", ".table", ".xml"}


class TuneParseError(ValueError):
    """Raised when TunerStudio tune data cannot be parsed as XML."""


@dataclass(frozen=True)
class TuneNode:
    tag: str
    attributes: dict[str, str]
    text: str | None
    children: tuple["TuneNode", ...]

    def find(self, tag: str) -> "TuneNode | None":
        for child in self.children:
            if child.tag == tag:
                return child
        return None

    def findall(self, tag: str) -> tuple["TuneNode", ...]:
        return tuple(child for child in self.children if child.tag == tag)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tag": self.tag,
            "attributes": dict(self.attributes),
            "text": self.text,
            "children": [child.to_dict() for child in self.children],
        }


@dataclass(frozen=True)
class Tune:
    root: TuneNode
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"source": self.source, "root": self.root.to_dict()}


def parse_tune(source: str | bytes | PathLike[str]) -> Tune:
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
        return parse_tune_file(path)

    return _parse_xml(source)


def parse_tune_file(path: str | PathLike[str]) -> Tune:
    file_path = Path(path).resolve(strict=False)
    return _parse_xml(file_path.read_bytes(), source=str(file_path))


def parse_tune_bytes(data: bytes) -> Tune:
    return _parse_xml(data)


def _looks_like_xml(source: str) -> bool:
    stripped = source.lstrip("\ufeff \t\r\n")
    return stripped.startswith("<?xml") or stripped.startswith("<")


def _looks_like_path(source: str) -> bool:
    return Path(source).suffix.lower() in PATH_SUFFIXES or "/" in source or "\\" in source


def _parse_xml(data: str | bytes, source: str | None = None) -> Tune:
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as exc:
        message = f"Invalid TunerStudio tune XML: {exc}"
        if source:
            message = f"{message} ({source})"
        raise TuneParseError(message) from exc

    return Tune(root=_build_node(root), source=source)


def _build_node(element: ElementTree.Element) -> TuneNode:
    text = element.text.strip() if element.text and element.text.strip() else None
    return TuneNode(
        tag=element.tag,
        attributes=dict(element.attrib),
        text=text,
        children=tuple(_build_node(child) for child in element),
    )
