from __future__ import annotations

from plant.adapter.inbound.api.schemas.notification_schema import NotificationDispatchResponse
from plant.app.dtos.notification_dto import NotificationResult


def to_response(result: NotificationResult) -> NotificationDispatchResponse:
    return NotificationDispatchResponse(
        id=result.id,
        plant_id=result.plant_id,
        channel=result.channel,
        message=result.message,
        coupang_link=result.coupang_link,
        delivery_status=result.delivery_status,
    )
