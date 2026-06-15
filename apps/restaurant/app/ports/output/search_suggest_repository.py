from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.search_suggest_dto import SearchSuggestQuery, SearchSuggestResponse


class SearchSuggestRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: SearchSuggestQuery) -> SearchSuggestResponse:
        pass
