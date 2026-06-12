from __future__ import annotations
from dataclasses import dataclass
from titanic.domain.value_objects.crew_andrews_architect_vo import AndrewsId, AndrewsName


@dataclass
class AndrewsArchitectEntity:
    """동등성은 domain_id 기준."""

    id: int
    domain_id: AndrewsId
    name: AndrewsName

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AndrewsArchitectEntity):
            return False
        return self.domain_id == other.domain_id

    def __hash__(self) -> int:
        return hash(self.domain_id)

    @classmethod
    def from_orm(cls, orm: object) -> "AndrewsArchitectEntity":
        return cls(
            id=orm.id,
            domain_id=AndrewsId(orm.id),
            name=AndrewsName(orm.name or "unknown"),
        )

    def full_name(self) -> str:
        return str(self.name)
