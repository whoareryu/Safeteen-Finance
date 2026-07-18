from __future__ import annotations

from abc import ABC, abstractmethod

from plant.domain.entities.photo_cache_entity import PhotoCacheEntity


class PhotoCacheRepository(ABC):
    """(species_name, growth_stage, status_key) 조합별 캐싱된 사진 조회/저장."""

    @abstractmethod
    async def find(self, species_name: str, growth_stage: str, status_key: str) -> PhotoCacheEntity | None:
        pass

    @abstractmethod
    async def save(self, entity: PhotoCacheEntity) -> PhotoCacheEntity:
        pass
