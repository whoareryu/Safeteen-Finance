from __future__ import annotations
from dataclasses import dataclass


@dataclass
class JamesDirectorEntity:
    """동등성은 id 기준."""

    id: int
    name: str
    scene_name: str
    description: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JamesDirectorEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_orm(cls, orm: object) -> "JamesDirectorEntity":
        return cls(
            id=orm.id,
            name=orm.name or "unknown",
            scene_name=orm.scene_name or "",
            description=orm.description or "",
        )

    def full_name(self) -> str:
        return self.name

    def has_scene(self) -> bool:
        return bool(self.scene_name and self.scene_name.strip())
