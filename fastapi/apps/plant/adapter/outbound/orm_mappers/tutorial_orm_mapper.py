from __future__ import annotations

from plant.adapter.outbound.orm.tutorial_plant_orm import TutorialPlantORM
from plant.domain.entities.tutorial_plant_entity import TutorialPlantEntity


def to_entity(orm: TutorialPlantORM) -> TutorialPlantEntity:
    return TutorialPlantEntity(
        id=orm.id,
        owner_user_id=orm.owner_user_id,
        species_name=orm.species_name,
        region=orm.region,
        growth_stage=orm.growth_stage,
        soil_moisture_pct=orm.soil_moisture_pct,
        nutrient_pct=orm.nutrient_pct,
        light_position=orm.light_position,
        points=orm.points,
        last_watered_at=orm.last_watered_at,
        last_fertilized_at=orm.last_fertilized_at,
        last_light_moved_at=orm.last_light_moved_at,
        last_weather_sync_at=orm.last_weather_sync_at,
        created_at=orm.created_at,
    )


def to_orm(entity: TutorialPlantEntity) -> TutorialPlantORM:
    return TutorialPlantORM(
        owner_user_id=entity.owner_user_id,
        species_name=entity.species_name,
        region=entity.region,
        growth_stage=entity.growth_stage,
        soil_moisture_pct=entity.soil_moisture_pct,
        nutrient_pct=entity.nutrient_pct,
        light_position=entity.light_position,
        points=entity.points,
        last_watered_at=entity.last_watered_at,
        last_fertilized_at=entity.last_fertilized_at,
        last_light_moved_at=entity.last_light_moved_at,
        last_weather_sync_at=entity.last_weather_sync_at,
    )
