from __future__ import annotations

from restaurant.app.dtos.category_catalog_dto import CategoryCatalogQuery, CategoryCatalogResponse
from restaurant.app.ports.output.category_catalog_repository import CategoryCatalogRepository


class CategoryCatalogPgRepository(CategoryCatalogRepository):
    async def introduce_myself(self, query: CategoryCatalogQuery) -> CategoryCatalogResponse:
        return CategoryCatalogResponse(id=query.id, name=query.name)
