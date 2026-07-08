from __future__ import annotations
from dataclasses import dataclass


@dataclass
class LoweBoatEntity:
    """동등성은 id 기준."""

    id: int
    name: str
    boat_number: str
    memo: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LoweBoatEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_orm(cls, orm: object) -> "LoweBoatEntity":
        return cls(
            id=orm.id,
            name=orm.name or "unknown",
            boat_number=orm.boat_number or "",
            memo=orm.memo or "",
        )

    def full_name(self) -> str:
        return self.name

    def has_lifeboat(self) -> bool:
        return bool(self.boat_number and self.boat_number.strip())
