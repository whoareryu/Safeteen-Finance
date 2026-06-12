from __future__ import annotations
from dataclasses import dataclass
from titanic.domain.value_objects.passenger_ruth_survivor_vo import RuthId, RuthName


@dataclass
class RuthSurvivorEntity:
    """동등성은 domain_id 기준."""

    id: int
    domain_id: RuthId
    name: RuthName

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuthSurvivorEntity):
            return False
        return self.domain_id == other.domain_id

    def __hash__(self) -> int:
        return hash(self.domain_id)

    @classmethod
    def from_orm(cls, orm: object) -> "RuthSurvivorEntity":
        return cls(
            id=orm.id,
            domain_id=RuthId(orm.id),
            name=RuthName(orm.name or "unknown"),
        )

    def full_name(self) -> str:
        return str(self.name)
