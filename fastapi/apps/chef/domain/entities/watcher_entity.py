from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WatcherEntity:
    id: int
    name: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WatcherEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def introduce_myself(self) -> str:
        return f"WatcherAgent(id={self.id}, name={self.name})"
