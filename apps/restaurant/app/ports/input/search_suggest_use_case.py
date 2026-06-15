from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.search_suggest_schema import SearchSuggestSchema
from restaurant.app.dtos.search_suggest_dto import SearchSuggestResponse


class SearchSuggestUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: SearchSuggestSchema) -> SearchSuggestResponse:
        pass
