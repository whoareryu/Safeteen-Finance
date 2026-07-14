from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.plant_checkin_entity import PlantCheckinEntity


class PlantCheckinRepository(ABC):

    @abstractmethod
    async def save(self, entity: PlantCheckinEntity) -> PlantCheckinEntity:
        pass

    @abstractmethod
    async def list_by_plant(self, plant_id: int) -> list[PlantCheckinEntity]:
        pass

    @abstractmethod
    async def count_by_plant(self, plant_id: int) -> int:
        pass
