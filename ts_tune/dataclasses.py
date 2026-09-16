'''Module dataclasses for TunerStudio tune representation.'''

from dataclasses import dataclass
from typing import Any

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


