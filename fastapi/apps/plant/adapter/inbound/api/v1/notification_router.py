from __future__ import annotations

from fastapi import APIRouter, Depends

from plant.adapter.inbound.mappers.notification_mapper import to_response
from plant.adapter.inbound.api.schemas.notification_schema import NotificationDispatchResponse
from plant.app.ports.input.notification_use_case import NotificationUseCase
from plant.dependencies.notification_provider import (
    get_notification_repository,
    get_notification_use_case,
)

notification_router = APIRouter(prefix="/notifications", tags=["plant-notifications"])


@notification_router.post("/dispatch", summary="특정 식물에 물주기 알림 즉시 발송(운영용)")
async def dispatch_notification(
    plant_id: int,
    use_case: NotificationUseCase = Depends(get_notification_use_case),
) -> NotificationDispatchResponse:
    result = await use_case.schedule(plant_id)
    return to_response(result)


@notification_router.get("", summary="식물별 알림 이력 조회")
async def list_notifications(
    plant_id: int,
    repository=Depends(get_notification_repository),
) -> list[NotificationDispatchResponse]:
    entities = await repository.find_by_plant(plant_id)
    return [
        NotificationDispatchResponse(
            id=entity.id,  # type: ignore[arg-type]
            plant_id=entity.plant_id,
            channel=entity.channel,
            message=entity.message,
            coupang_link=entity.coupang_link,
            delivery_status=entity.delivery_status,
        )
        for entity in entities
    ]
