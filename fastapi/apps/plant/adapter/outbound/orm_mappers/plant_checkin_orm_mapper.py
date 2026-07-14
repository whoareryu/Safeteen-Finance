from __future__ import annotations

from plant.adapter.outbound.orm.plant_checkin_orm import PlantCheckinORM
from plant.domain.entities.plant_checkin_entity import PlantCheckinEntity


def to_entity(orm: PlantCheckinORM) -> PlantCheckinEntity:
    return PlantCheckinEntity(
        id=orm.id,
        plant_id=orm.plant_id,
        photo_url=orm.photo_url,
        checkin_date=orm.checkin_date,
        health_score=orm.health_score,
        points_earned=orm.points_earned,
        streak_day=orm.streak_day,
        created_at=orm.created_at,
    )


def to_orm(entity: PlantCheckinEntity) -> PlantCheckinORM:
    return PlantCheckinORM(
        plant_id=entity.plant_id,
        photo_url=entity.photo_url,
        checkin_date=entity.checkin_date,
        health_score=entity.health_score,
        points_earned=entity.points_earned,
        streak_day=entity.streak_day,
    )
