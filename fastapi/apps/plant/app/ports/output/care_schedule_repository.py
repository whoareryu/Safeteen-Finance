from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.care_schedule_entity import CareScheduleEntity


class CareScheduleRepository(ABC):

    @abstractmethod
    async def find_due(self, region: str) -> list[CareScheduleEntity]:
        pass

    @abstractmethod
    async def save(self, entity: CareScheduleEntity) -> CareScheduleEntity:
        pass

    @abstractmethod
    async def mark_watered(self, plant_id: int) -> None:
        pass
