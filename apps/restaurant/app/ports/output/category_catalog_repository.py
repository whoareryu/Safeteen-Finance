from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.category_catalog_dto import CategoryCatalogQuery, CategoryCatalogResponse


class CategoryCatalogRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: CategoryCatalogQuery) -> CategoryCatalogResponse:
        pass
