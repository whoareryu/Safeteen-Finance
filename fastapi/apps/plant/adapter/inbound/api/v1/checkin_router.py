from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from plant.adapter.inbound.mappers.checkin_mapper import to_response
from plant.adapter.inbound.api.schemas.checkin_schema import CheckinHistoryItem, CheckinResponse
from plant.app.dtos.checkin_dto import CheckinCommand
from plant.app.ports.input.checkin_use_case import CheckinUseCase
from plant.app.ports.output.plant_checkin_repository import PlantCheckinRepository
from plant.dependencies.checkin_provider import get_checkin_repository, get_checkin_use_case

checkin_router = APIRouter(prefix="/my-plants", tags=["plant-checkin"])


@checkin_router.post("/{plant_id}/checkin", summary="일일 출석체크 — 사진으로 건강도·포인트·스트릭 갱신")
async def checkin(
    plant_id: int,
    file: UploadFile = File(...),
    use_case: CheckinUseCase = Depends(get_checkin_use_case),
) -> CheckinResponse:
    content = await file.read()
    command = CheckinCommand(
        plant_id=plant_id,
        photo_data=content,
        photo_filename=file.filename or "checkin.jpg",
        photo_content_type=file.content_type or "application/octet-stream",
    )
    try:
        result = await use_case.checkin(command)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    return to_response(result)


@checkin_router.get("/{plant_id}/checkins", summary="출석체크 이력 조회")
async def list_checkins(
    plant_id: int,
    repository: PlantCheckinRepository = Depends(get_checkin_repository),
) -> list[CheckinHistoryItem]:
    entities = await repository.list_by_plant(plant_id)
    return [
        CheckinHistoryItem(
            id=e.id,  # type: ignore[arg-type]
            photo_url=e.photo_url,
            checkin_date=e.checkin_date,
            health_score=e.health_score,
            points_earned=e.points_earned,
            streak_day=e.streak_day,
        )
        for e in entities
    ]
