from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.notification_dto import NotificationResult
from plant.domain.entities.weather_snapshot_entity import WeatherSnapshotEntity


class NotificationUseCase(ABC):
    """Inbound 입력 포트 — 물주기 알림 발송."""

    @abstractmethod
    async def schedule(self, plant_id: int) -> NotificationResult:
        pass

    @abstractmethod
    async def dispatch_for_region(
        self, region: str, snapshot: WeatherSnapshotEntity
    ) -> list[NotificationResult]:
        pass
