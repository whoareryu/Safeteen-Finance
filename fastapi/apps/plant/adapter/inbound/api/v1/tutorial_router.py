from __future__ import annotations

from fastapi import APIRouter, Depends

from plant.adapter.inbound.mappers.tutorial_mapper import (
    to_create_command,
    to_move_light_command,
    to_response,
)
from plant.adapter.inbound.api.schemas.tutorial_schema import (
    TutorialCreateRequest,
    TutorialMoveLightRequest,
    TutorialStateResponse,
)
from plant.app.ports.input.tutorial_use_case import TutorialUseCase
from plant.dependencies.tutorial_provider import get_tutorial_use_case

tutorial_router = APIRouter(prefix="/tutorial", tags=["plant-tutorial"])


@tutorial_router.post("", summary="식집사 튜토리얼 식물 새로 심기")
async def create_tutorial(
    request: TutorialCreateRequest,
    use_case: TutorialUseCase = Depends(get_tutorial_use_case),
) -> TutorialStateResponse:
    result = await use_case.create(to_create_command(request))
    return to_response(result)


@tutorial_router.get("/active", summary="사용자의 진행 중인 튜토리얼 식물 조회")
async def get_active_tutorial(
    owner_user_id: int,
    use_case: TutorialUseCase = Depends(get_tutorial_use_case),
) -> TutorialStateResponse | None:
    result = await use_case.get_active_for_owner(owner_user_id)
    return to_response(result) if result is not None else None


@tutorial_router.get("/{tutorial_plant_id}", summary="튜토리얼 식물 상태 조회")
async def get_tutorial(
    tutorial_plant_id: int,
    use_case: TutorialUseCase = Depends(get_tutorial_use_case),
) -> TutorialStateResponse:
    result = await use_case.get(tutorial_plant_id)
    return to_response(result)


@tutorial_router.post("/{tutorial_plant_id}/water", summary="물주기")
async def water_tutorial(
    tutorial_plant_id: int,
    use_case: TutorialUseCase = Depends(get_tutorial_use_case),
) -> TutorialStateResponse:
    result = await use_case.water(tutorial_plant_id)
    return to_response(result)


@tutorial_router.post("/{tutorial_plant_id}/nutrient", summary="영양제 주기")
async def add_nutrient_tutorial(
    tutorial_plant_id: int,
    use_case: TutorialUseCase = Depends(get_tutorial_use_case),
) -> TutorialStateResponse:
    result = await use_case.add_nutrient(tutorial_plant_id)
    return to_response(result)


@tutorial_router.post("/{tutorial_plant_id}/move-light", summary="햇빛 자리로 이동")
async def move_light_tutorial(
    tutorial_plant_id: int,
    request: TutorialMoveLightRequest,
    use_case: TutorialUseCase = Depends(get_tutorial_use_case),
) -> TutorialStateResponse:
    result = await use_case.move_light(to_move_light_command(tutorial_plant_id, request))
    return to_response(result)


@tutorial_router.get("/{tutorial_plant_id}/check-leaves", summary="잎사귀 확인 (상태 변화 없음)")
async def check_leaves_tutorial(
    tutorial_plant_id: int,
    use_case: TutorialUseCase = Depends(get_tutorial_use_case),
) -> TutorialStateResponse:
    result = await use_case.check_leaves(tutorial_plant_id)
    return to_response(result)
