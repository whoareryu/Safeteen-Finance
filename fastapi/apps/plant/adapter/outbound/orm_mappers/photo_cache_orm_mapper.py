from __future__ import annotations

from plant.adapter.outbound.orm.pixabay_photo_cache_orm import PixabayPhotoCacheORM
from plant.domain.entities.photo_cache_entity import PhotoCacheEntity


def to_entity(orm: PixabayPhotoCacheORM) -> PhotoCacheEntity:
    return PhotoCacheEntity(
        id=orm.id,
        species_name=orm.species_name,
        growth_stage=orm.growth_stage,
        status_key=orm.status_key,
        image_url=orm.image_url,
        pixabay_source_id=orm.pixabay_source_id,
        fetched_at=orm.fetched_at,
    )


def to_orm(entity: PhotoCacheEntity) -> PixabayPhotoCacheORM:
    return PixabayPhotoCacheORM(
        species_name=entity.species_name,
        growth_stage=entity.growth_stage,
        status_key=entity.status_key,
        image_url=entity.image_url,
        pixabay_source_id=entity.pixabay_source_id,
    )
