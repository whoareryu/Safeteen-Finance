from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.tutorial_plant_entity import TutorialPlantEntity


class TutorialRepository(ABC):

    @abstractmethod
    async def save(self, entity: TutorialPlantEntity) -> TutorialPlantEntity:
        pass

    @abstractmethod
    async def get(self, tutorial_plant_id: int) -> TutorialPlantEntity:
        pass

    @abstractmethod
    async def get_by_owner(self, owner_user_id: int) -> TutorialPlantEntity | None:
        pass

    @abstractmethod
    async def update(self, entity: TutorialPlantEntity) -> TutorialPlantEntity:
        pass
