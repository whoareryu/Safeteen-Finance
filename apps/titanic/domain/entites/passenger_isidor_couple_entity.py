from __future__ import annotations
from dataclasses import dataclass
from titanic.domain.value_objects.passenger_isidor_couple_vo import IsidorId, IsidorName


@dataclass
class IsidorCoupleEntity:
    """동등성은 domain_id 기준."""

    id: int
    domain_id: IsidorId
    name: IsidorName

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IsidorCoupleEntity):
            return False
        return self.domain_id == other.domain_id

    def __hash__(self) -> int:
        return hash(self.domain_id)

    @classmethod
    def from_orm(cls, orm: object) -> "IsidorCoupleEntity":
        return cls(
            id=orm.id,
            domain_id=IsidorId(orm.id),
            name=IsidorName(orm.name or "unknown"),
        )

    def full_name(self) -> str:
        return str(self.name)
