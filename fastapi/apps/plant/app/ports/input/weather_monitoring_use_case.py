from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.weather_dto import WeatherIngestCommand, WeatherSnapshotResult


class WeatherMonitoringUseCase(ABC):
    """Inbound 입력 포트 — 지역별 날씨 수신 및 건조일 판정."""

    @abstractmethod
    async def ingest(self, command: WeatherIngestCommand) -> WeatherSnapshotResult:
        pass

    @abstractmethod
    async def get_current(self, region: str) -> WeatherSnapshotResult:
        pass
