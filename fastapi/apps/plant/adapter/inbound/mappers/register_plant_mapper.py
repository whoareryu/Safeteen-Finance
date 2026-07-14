from __future__ import annotations

from plant.adapter.inbound.api.schemas.register_plant_schema import MyPlantResponse
from plant.app.dtos.register_plant_dto import RegisterPlantResult
from plant.domain.entities.plant_entity import PlantEntity


def to_response(result: RegisterPlantResult) -> MyPlantResponse:
    return MyPlantResponse(
        id=result.id,
        nickname=result.nickname,
        species_name=result.species_name,
        region=result.region,
        growth_stage=result.growth_stage,
        points=result.points,
    )


def entity_to_response(entity: PlantEntity) -> MyPlantResponse:
    return MyPlantResponse(
        id=entity.id,  # type: ignore[arg-type]
        nickname=entity.nickname,
        species_name=entity.species_name,
        region=entity.region,
        growth_stage=entity.growth_stage,
        points=entity.points,
        streak_count=entity.streak_count,
    )
