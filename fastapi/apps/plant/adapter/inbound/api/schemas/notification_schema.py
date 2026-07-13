from __future__ import annotations

from pydantic import BaseModel


class NotificationDispatchResponse(BaseModel):
    id: int
    plant_id: int | None
    channel: str
    message: str
    coupang_link: str | None
    delivery_status: str
