from __future__ import annotations
from dataclasses import dataclass
from titanic.domain.value_objects.passenger_cal_tester_vo import CalId, CalName


@dataclass
class CalTesterEntity:
    """동등성은 domain_id 기준."""

    id: int
    domain_id: CalId
    name: CalName

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CalTesterEntity):
            return False
        return self.domain_id == other.domain_id

    def __hash__(self) -> int:
        return hash(self.domain_id)

    @classmethod
    def from_orm(cls, orm: object) -> "CalTesterEntity":
        return cls(
            id=orm.id,
            domain_id=CalId(orm.id),
            name=CalName(orm.name or "unknown"),
        )

    def full_name(self) -> str:
        return str(self.name)
