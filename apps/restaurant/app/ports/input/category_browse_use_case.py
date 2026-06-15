from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.category_browse_schema import CategoryBrowseSchema
from restaurant.app.dtos.category_browse_dto import CategoryBrowseResponse


class CategoryBrowseUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: CategoryBrowseSchema) -> CategoryBrowseResponse:
        pass
