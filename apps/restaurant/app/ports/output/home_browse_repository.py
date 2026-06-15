from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.home_browse_dto import HomeBrowseQuery, HomeBrowseResponse


class HomeBrowseRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: HomeBrowseQuery) -> HomeBrowseResponse:
        pass
