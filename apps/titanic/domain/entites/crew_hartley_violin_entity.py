from __future__ import annotations
from dataclasses import dataclass
from titanic.domain.value_objects.crew_hartley_violin_vo import HartleyId, HartleyName


@dataclass
class HartleyViolinEntity:
    """동등성은 domain_id 기준."""

    id: int
    domain_id: HartleyId
    name: HartleyName

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HartleyViolinEntity):
            return False
        return self.domain_id == other.domain_id

    def __hash__(self) -> int:
        return hash(self.domain_id)

    @classmethod
    def from_orm(cls, orm: object) -> "HartleyViolinEntity":
        return cls(
            id=orm.id,
            domain_id=HartleyId(orm.id),
            name=HartleyName(orm.name or "unknown"),
        )

    def full_name(self) -> str:
        return str(self.name)
