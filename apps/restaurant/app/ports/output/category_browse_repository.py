from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.category_browse_dto import CategoryBrowseQuery, CategoryBrowseResponse


class CategoryBrowseRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: CategoryBrowseQuery) -> CategoryBrowseResponse:
        pass
