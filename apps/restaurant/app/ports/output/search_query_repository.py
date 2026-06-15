from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.search_query_dto import SearchQueryQuery, SearchQueryResponse


class SearchQueryRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: SearchQueryQuery) -> SearchQueryResponse:
        pass
