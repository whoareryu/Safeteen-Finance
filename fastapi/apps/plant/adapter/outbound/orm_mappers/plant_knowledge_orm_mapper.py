from __future__ import annotations

from plant.adapter.outbound.orm.plant_knowledge_orm import PlantKnowledgeORM
from plant.domain.entities.plant_knowledge_entity import PlantKnowledgeEntity


def to_entity(orm: PlantKnowledgeORM) -> PlantKnowledgeEntity:
    return PlantKnowledgeEntity(
        id=orm.id,
        category=orm.category,
        name=orm.name,
        description=orm.description,
    )
