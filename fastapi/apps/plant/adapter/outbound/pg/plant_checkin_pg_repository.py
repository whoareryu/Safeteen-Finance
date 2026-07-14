from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.plant_checkin_orm import PlantCheckinORM
from plant.adapter.outbound.orm_mappers.plant_checkin_orm_mapper import to_entity, to_orm
from plant.app.ports.output.plant_checkin_repository import PlantCheckinRepository
from plant.domain.entities.plant_checkin_entity import PlantCheckinEntity


class PlantCheckinPgRepository(PlantCheckinRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, entity: PlantCheckinEntity) -> PlantCheckinEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def list_by_plant(self, plant_id: int) -> list[PlantCheckinEntity]:
        stmt = (
            select(PlantCheckinORM)
            .where(PlantCheckinORM.plant_id == plant_id)
            .order_by(PlantCheckinORM.checkin_date.desc())
        )
        result = await self.session.execute(stmt)
        return [to_entity(orm) for orm in result.scalars().all()]

    async def count_by_plant(self, plant_id: int) -> int:
        stmt = select(func.count()).select_from(PlantCheckinORM).where(
            PlantCheckinORM.plant_id == plant_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
