from __future__ import annotations
from dataclasses import dataclass
from titanic.domain.value_objects.crew_smith_captain_vo import SmithId, SmithName


@dataclass
class SmithCaptainEntity:
    """동등성은 domain_id 기준."""

    id: int
    domain_id: SmithId
    name: SmithName

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SmithCaptainEntity):
            return False
        return self.domain_id == other.domain_id

    def __hash__(self) -> int:
        return hash(self.domain_id)

    @classmethod
    def from_orm(cls, orm: object) -> "SmithCaptainEntity":
        return cls(
            id=orm.id,
            domain_id=SmithId(orm.id),
            name=SmithName(orm.name or "unknown"),
        )

    def full_name(self) -> str:
        return str(self.name)
