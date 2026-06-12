from __future__ import annotations
from dataclasses import dataclass
from titanic.domain.value_objects.crew_james_director_vo import JamesId, JamesName, SceneDescription, SceneName


@dataclass
class JamesDirectorEntity:
    """동등성은 domain_id 기준."""

    id: int
    domain_id: JamesId
    name: JamesName
    scene_name: SceneName
    description: SceneDescription

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JamesDirectorEntity):
            return False
        return self.domain_id == other.domain_id

    def __hash__(self) -> int:
        return hash(self.domain_id)

    @classmethod
    def from_orm(cls, orm: object) -> "JamesDirectorEntity":
        return cls(
            id=orm.id,
            domain_id=JamesId(orm.id),
            name=JamesName(orm.name or "unknown"),
            scene_name=SceneName(orm.scene_name or ""),
            description=SceneDescription(orm.description or ""),
        )

    def full_name(self) -> str:
        return str(self.name)

    def has_scene(self) -> bool:
        return self.scene_name.is_known()
