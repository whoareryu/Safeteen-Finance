from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.weather_snapshot_entity import WeatherSnapshotEntity


class WeatherSnapshotRepository(ABC):

    @abstractmethod
    async def save(self, entity: WeatherSnapshotEntity) -> WeatherSnapshotEntity:
        pass

    @abstractmethod
    async def find_latest(self, region: str) -> WeatherSnapshotEntity | None:
        pass
