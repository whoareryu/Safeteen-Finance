from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.weather_snapshot_orm import WeatherSnapshotORM
from plant.adapter.outbound.orm_mappers.weather_snapshot_orm_mapper import to_entity, to_orm
from plant.app.ports.output.weather_snapshot_repository import WeatherSnapshotRepository
from plant.domain.entities.weather_snapshot_entity import WeatherSnapshotEntity


class WeatherSnapshotPgRepository(WeatherSnapshotRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, entity: WeatherSnapshotEntity) -> WeatherSnapshotEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)

    async def find_latest(self, region: str) -> WeatherSnapshotEntity | None:
        query = (
            select(WeatherSnapshotORM)
            .where(WeatherSnapshotORM.region == region)
            .order_by(WeatherSnapshotORM.recorded_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        orm = result.scalar_one_or_none()
        return to_entity(orm) if orm is not None else None
