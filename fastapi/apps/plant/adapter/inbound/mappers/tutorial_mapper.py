from __future__ import annotations

from plant.adapter.inbound.api.schemas.tutorial_schema import (
    TutorialCreateRequest,
    TutorialMoveLightRequest,
    TutorialStateResponse,
)
from plant.app.dtos.tutorial_dto import (
    TutorialCreateCommand,
    TutorialMoveLightCommand,
    TutorialStateResult,
)


def to_create_command(request: TutorialCreateRequest) -> TutorialCreateCommand:
    return TutorialCreateCommand(
        owner_user_id=request.owner_user_id,
        species_name=request.species_name,
        region=request.region,
    )


def to_move_light_command(tutorial_plant_id: int, request: TutorialMoveLightRequest) -> TutorialMoveLightCommand:
    return TutorialMoveLightCommand(
        tutorial_plant_id=tutorial_plant_id,
        light_position=request.light_position,
    )


def to_response(result: TutorialStateResult) -> TutorialStateResponse:
    return TutorialStateResponse(
        id=result.id,
        owner_user_id=result.owner_user_id,
        species_name=result.species_name,
        region=result.region,
        growth_stage=result.growth_stage,
        soil_moisture_pct=result.soil_moisture_pct,
        nutrient_pct=result.nutrient_pct,
        light_position=result.light_position,
        points=result.points,
        status=result.status,
        photo_url=result.photo_url,
        feedback=result.feedback,
    )
