from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.notification_event_orm import NotificationEventORM
from plant.adapter.outbound.orm_mappers.notification_event_orm_mapper import to_entity, to_orm
from plant.app.ports.output.notification_repository import NotificationRepository
from plant.domain.entities.notification_event_entity import NotificationEventEntity


class NotificationPgRepository(NotificationRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, entity: NotificationEventEntity) -> NotificationEventEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def find_by_plant(self, plant_id: int) -> list[NotificationEventEntity]:
        query = select(NotificationEventORM).where(NotificationEventORM.plant_id == plant_id)
        result = await self.session.execute(query)
        return [to_entity(orm) for orm in result.scalars().all()]
