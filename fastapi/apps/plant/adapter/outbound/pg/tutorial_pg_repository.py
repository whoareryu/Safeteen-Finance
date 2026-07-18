from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.tutorial_plant_orm import TutorialPlantORM
from plant.adapter.outbound.orm_mappers.tutorial_orm_mapper import to_entity, to_orm
from plant.app.ports.output.tutorial_repository import TutorialRepository
from plant.domain.entities.tutorial_plant_entity import TutorialPlantEntity


class TutorialPgRepository(TutorialRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, entity: TutorialPlantEntity) -> TutorialPlantEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def get(self, tutorial_plant_id: int) -> TutorialPlantEntity:
        orm = await self.session.get(TutorialPlantORM, tutorial_plant_id)
        if orm is None:
            raise ValueError(f"Tutorial plant {tutorial_plant_id} not found")
        return to_entity(orm)

    async def get_by_owner(self, owner_user_id: int) -> TutorialPlantEntity | None:
        query = (
            select(TutorialPlantORM)
            .where(TutorialPlantORM.owner_user_id == owner_user_id)
            .order_by(TutorialPlantORM.created_at.desc())
        )
        result = await self.session.execute(query)
        orm = result.scalars().first()
        return to_entity(orm) if orm is not None else None

    async def update(self, entity: TutorialPlantEntity) -> TutorialPlantEntity:
        orm = await self.session.get(TutorialPlantORM, entity.id)
        if orm is None:
            raise ValueError(f"Tutorial plant {entity.id} not found")
        orm.growth_stage = entity.growth_stage
        orm.soil_moisture_pct = entity.soil_moisture_pct
        orm.nutrient_pct = entity.nutrient_pct
        orm.light_position = entity.light_position
        orm.points = entity.points
        orm.last_watered_at = entity.last_watered_at
        orm.last_fertilized_at = entity.last_fertilized_at
        orm.last_light_moved_at = entity.last_light_moved_at
        orm.last_weather_sync_at = entity.last_weather_sync_at
        await self.session.flush()
        return to_entity(orm)
