from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.care_schedule_orm import CareScheduleORM
from plant.adapter.outbound.orm.plant_orm import PlantORM
from plant.adapter.outbound.orm_mappers.care_schedule_orm_mapper import to_entity, to_orm
from plant.app.ports.output.care_schedule_repository import CareScheduleRepository
from plant.domain.entities.care_schedule_entity import CareScheduleEntity


class CareSchedulePgRepository(CareScheduleRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_due(self, region: str) -> list[CareScheduleEntity]:
        query = (
            select(CareScheduleORM)
            .join(PlantORM, PlantORM.id == CareScheduleORM.plant_id)
            .where(
                PlantORM.region == region,
                CareScheduleORM.status == "active",
                CareScheduleORM.next_watering_due_at <= datetime.now(timezone.utc),
            )
        )
        result = await self.session.execute(query)
        return [to_entity(orm) for orm in result.scalars().all()]

    async def get_by_plant(self, plant_id: int) -> CareScheduleEntity | None:
        query = select(CareScheduleORM).where(CareScheduleORM.plant_id == plant_id)
        result = await self.session.execute(query)
        orm = result.scalar_one_or_none()
        return to_entity(orm) if orm is not None else None

    async def save(self, entity: CareScheduleEntity) -> CareScheduleEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def mark_watered(self, plant_id: int) -> None:
        query = select(CareScheduleORM).where(CareScheduleORM.plant_id == plant_id)
        result = await self.session.execute(query)
        orm = result.scalar_one_or_none()
        if orm is not None:
            orm.last_watered_at = datetime.now(timezone.utc)
