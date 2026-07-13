from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NotificationSendDto:
    channel: str
    message: str
    coupang_link: str | None


@dataclass(frozen=True)
class NotificationResult:
    id: int
    plant_id: int | None
    channel: str
    message: str
    coupang_link: str | None
    delivery_status: str
