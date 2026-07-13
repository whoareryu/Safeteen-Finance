from __future__ import annotations

from plant.adapter.outbound.orm.plant_orm import PlantORM
from plant.domain.entities.plant_entity import PlantEntity


def to_entity(orm: PlantORM) -> PlantEntity:
    return PlantEntity(
        id=orm.id,
        owner_user_id=orm.owner_user_id,
        nickname=orm.nickname,
        species_name=orm.species_name,
        region=orm.region,
        created_at=orm.created_at,
    )


def to_orm(entity: PlantEntity) -> PlantORM:
    return PlantORM(
        owner_user_id=entity.owner_user_id,
        nickname=entity.nickname,
        species_name=entity.species_name,
        region=entity.region,
    )
