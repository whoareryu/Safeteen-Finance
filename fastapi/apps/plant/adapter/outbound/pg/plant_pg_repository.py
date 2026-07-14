from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.plant_orm import PlantORM
from plant.adapter.outbound.orm_mappers.plant_orm_mapper import to_entity, to_orm
from plant.app.ports.output.plant_repository import PlantRepository
from plant.domain.entities.plant_entity import PlantEntity


class PlantPgRepository(PlantRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_or_create(
        self, owner_user_id: int | None, region: str, species_hint: str
    ) -> PlantEntity:
        query = select(PlantORM).where(
            PlantORM.owner_user_id == owner_user_id,
            PlantORM.region == region,
            PlantORM.species_name == species_hint,
        )
        result = await self.session.execute(query)
        existing = result.scalar_one_or_none()
        if existing is not None:
            return to_entity(existing)

        orm = to_orm(
            PlantEntity(
                id=None,
                owner_user_id=owner_user_id,
                nickname=species_hint,
                species_name=species_hint,
                region=region,
            )
        )
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def register(self, entity: PlantEntity) -> PlantEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def list_by_owner(self, owner_user_id: int | None) -> list[PlantEntity]:
        stmt = (
            select(PlantORM)
            .where(PlantORM.owner_user_id == owner_user_id)
            .order_by(PlantORM.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [to_entity(orm) for orm in result.scalars().all()]

    async def get(self, plant_id: int) -> PlantEntity:
        orm = await self.session.get(PlantORM, plant_id)
        if orm is None:
            raise ValueError(f"Plant {plant_id} not found")
        return to_entity(orm)

    async def update(self, entity: PlantEntity) -> PlantEntity:
        orm = await self.session.get(PlantORM, entity.id)
        if orm is None:
            raise ValueError(f"Plant {entity.id} not found")
        orm.growth_stage = entity.growth_stage
        orm.points = entity.points
        orm.streak_count = entity.streak_count
        orm.last_checkin_date = entity.last_checkin_date
        await self.session.flush()
        return to_entity(orm)
