from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NotificationEventEntity:
    id: int | None
    plant_id: int | None
    channel: str
    message: str
    coupang_link: str | None
    triggered_by: str
    delivery_status: str = "pending"
    sent_at: datetime | None = None
