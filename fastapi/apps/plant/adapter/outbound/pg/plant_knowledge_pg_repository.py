from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.plant_knowledge_orm import PlantKnowledgeORM
from plant.adapter.outbound.orm_mappers.plant_knowledge_orm_mapper import to_entity
from plant.app.ports.output.plant_knowledge_repository import PlantKnowledgeRepository
from plant.domain.entities.plant_knowledge_entity import PlantKnowledgeEntity


class PlantKnowledgePgRepository(PlantKnowledgeRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_similar(self, embedding: list[float], limit: int) -> list[PlantKnowledgeEntity]:
        stmt = (
            select(PlantKnowledgeORM)
            .where(PlantKnowledgeORM.embedding.is_not(None))
            .order_by(PlantKnowledgeORM.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [to_entity(orm) for orm in result.scalars().all()]
