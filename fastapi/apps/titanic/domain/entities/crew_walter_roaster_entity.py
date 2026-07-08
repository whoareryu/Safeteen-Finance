from __future__ import annotations
from dataclasses import dataclass


@dataclass
class WalterRoasterEntity:
    """동등성은 id 기준."""

    id: int
    name: str
    memo: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WalterRoasterEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def from_orm(cls, orm: object) -> "WalterRoasterEntity":
        return cls(
            id=orm.id,
            name=orm.name or "unknown",
            memo=orm.memo or "",
        )

    def full_name(self) -> str:
        return self.name

    def has_memo(self) -> bool:
        return bool(self.memo.strip())
