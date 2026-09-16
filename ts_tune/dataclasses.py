'''Module dataclasses for TunerStudio tune representation.'''

from types import MappingProxyType
from dataclasses import dataclass
from typing import Any, Mapping

@dataclass(frozen=True)
class TuneNode:
    """Node in a parsed TunerStudio XML tree."""

    tag: str
    attributes: Mapping[str, str]
    text: str | None
    children: tuple["TuneNode", ...]

    def find(self, tag: str) -> "TuneNode | None":
        """Return the first direct child node matching ``tag``."""

        for child in self.children:
            if child.tag == tag:
                return child
        return None

    def findall(self, tag: str) -> tuple["TuneNode", ...]:
        """Return all direct child nodes matching ``tag``."""

        return tuple(child for child in self.children if child.tag == tag)

    def to_dict(self) -> dict[str, Any]:
        """Convert the node and its descendants into built-in containers."""

        return {
            "tag": self.tag,
            "attributes": dict(self.attributes),
            "text": self.text,
            "children": [child.to_dict() for child in self.children],
        }


@dataclass(frozen=True)
class Tune:
    """Parsed TunerStudio tune with its root XML node and optional source."""

    root: TuneNode
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the tune to a dictionary that preserves source metadata."""

        return {"source": self.source, "root": self.root.to_dict()}


def freeze_attributes(attributes: dict[str, str]) -> Mapping[str, str]:
    """Return a read-only mapping for XML element attributes."""

    return MappingProxyType(dict(attributes))
