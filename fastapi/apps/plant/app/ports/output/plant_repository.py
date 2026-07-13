from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.plant_entity import PlantEntity


class PlantRepository(ABC):

    @abstractmethod
    async def find_or_create(
        self, owner_user_id: int | None, region: str, species_hint: str
    ) -> PlantEntity:
        pass

    @abstractmethod
    async def get(self, plant_id: int) -> PlantEntity:
        pass
