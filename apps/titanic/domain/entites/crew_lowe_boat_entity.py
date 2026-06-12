from __future__ import annotations
from dataclasses import dataclass
from titanic.domain.value_objects.crew_lowe_boat_vo import BoatNumber, LoweId, LoweMemo, LoweName


@dataclass
class LoweBoatEntity:
    """동등성은 domain_id 기준."""

    id: int
    domain_id: LoweId
    name: LoweName
    boat_number: BoatNumber
    memo: LoweMemo

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LoweBoatEntity):
            return False
        return self.domain_id == other.domain_id

    def __hash__(self) -> int:
        return hash(self.domain_id)

    @classmethod
    def from_orm(cls, orm: object) -> "LoweBoatEntity":
        return cls(
            id=orm.id,
            domain_id=LoweId(orm.id),
            name=LoweName(orm.name or "unknown"),
            boat_number=BoatNumber(orm.boat_number or ""),
            memo=LoweMemo(orm.memo or ""),
        )

    def full_name(self) -> str:
        return str(self.name)

    def has_lifeboat(self) -> bool:
        return self.boat_number.is_known()
