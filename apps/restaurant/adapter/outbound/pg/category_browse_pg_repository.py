from __future__ import annotations

from restaurant.app.dtos.category_browse_dto import CategoryBrowseQuery, CategoryBrowseResponse
from restaurant.app.ports.output.category_browse_repository import CategoryBrowseRepository


class CategoryBrowsePgRepository(CategoryBrowseRepository):
    async def introduce_myself(self, query: CategoryBrowseQuery) -> CategoryBrowseResponse:
        return CategoryBrowseResponse(id=query.id, name=query.name)
