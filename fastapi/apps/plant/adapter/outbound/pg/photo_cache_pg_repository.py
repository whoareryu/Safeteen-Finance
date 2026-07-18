from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from plant.adapter.outbound.orm.pixabay_photo_cache_orm import PixabayPhotoCacheORM
from plant.adapter.outbound.orm_mappers.photo_cache_orm_mapper import to_entity, to_orm
from plant.app.ports.output.photo_cache_repository import PhotoCacheRepository
from plant.domain.entities.photo_cache_entity import PhotoCacheEntity


class PhotoCachePgRepository(PhotoCacheRepository):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find(self, species_name: str, growth_stage: str, status_key: str) -> PhotoCacheEntity | None:
        query = select(PixabayPhotoCacheORM).where(
            PixabayPhotoCacheORM.species_name == species_name,
            PixabayPhotoCacheORM.growth_stage == growth_stage,
            PixabayPhotoCacheORM.status_key == status_key,
        )
        result = await self.session.execute(query)
        orm = result.scalar_one_or_none()
        return to_entity(orm) if orm is not None else None

    async def save(self, entity: PhotoCacheEntity) -> PhotoCacheEntity:
        orm = to_orm(entity)
        self.session.add(orm)
        await self.session.flush()
        return to_entity(orm)
