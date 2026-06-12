from __future__ import annotations
from dataclasses import dataclass
from titanic.domain.value_objects.crew_walter_roaster_vo import WalterId, WalterMemo, WalterName


@dataclass
class WalterRoasterEntity:
    """동등성은 domain_id 기준."""

    id: int
    domain_id: WalterId
    name: WalterName
    memo: WalterMemo

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WalterRoasterEntity):
            return False
        return self.domain_id == other.domain_id

    def __hash__(self) -> int:
        return hash(self.domain_id)

    @classmethod
    def from_orm(cls, orm: object) -> "WalterRoasterEntity":
        return cls(
            id=orm.id,
            domain_id=WalterId(orm.id),
            name=WalterName(orm.name or "unknown"),
            memo=WalterMemo(orm.memo or ""),
        )

    def full_name(self) -> str:
        return str(self.name)

    def has_memo(self) -> bool:
        return not self.memo.is_empty()
