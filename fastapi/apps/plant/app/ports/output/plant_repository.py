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
    async def register(self, entity: PlantEntity) -> PlantEntity:
        """마이플랜트 명시적 등록 — 중복 체크 없이 항상 새로 생성."""
        pass

    @abstractmethod
    async def list_by_owner(self, owner_user_id: int | None) -> list[PlantEntity]:
        pass

    @abstractmethod
    async def get(self, plant_id: int) -> PlantEntity:
        pass

    @abstractmethod
    async def update(self, entity: PlantEntity) -> PlantEntity:
        pass
