from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.plant_badge_entity import EarnedBadgeEntity, PlantBadgeEntity


class BadgeRepository(ABC):
    """뱃지 카탈로그 조회 및 획득 처리."""

    @abstractmethod
    async def list_catalog(self) -> list[PlantBadgeEntity]:
        pass

    @abstractmethod
    async def list_earned(self, plant_id: int) -> list[EarnedBadgeEntity]:
        pass

    @abstractmethod
    async def award_if_missing(self, plant_id: int, code: str) -> bool:
        """이미 획득한 뱃지면 False, 새로 획득했으면 True."""
        pass
