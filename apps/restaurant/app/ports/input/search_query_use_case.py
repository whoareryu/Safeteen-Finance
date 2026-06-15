from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.search_query_schema import SearchQuerySchema
from restaurant.app.dtos.search_query_dto import SearchQueryResponse


class SearchQueryUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: SearchQuerySchema) -> SearchQueryResponse:
        pass
