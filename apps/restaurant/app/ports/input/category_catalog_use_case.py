from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.category_catalog_schema import CategoryCatalogSchema
from restaurant.app.dtos.category_catalog_dto import CategoryCatalogResponse


class CategoryCatalogUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: CategoryCatalogSchema) -> CategoryCatalogResponse:
        pass
