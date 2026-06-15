from __future__ import annotations

from restaurant.app.dtos.search_suggest_dto import SearchSuggestQuery, SearchSuggestResponse
from restaurant.app.ports.output.search_suggest_repository import SearchSuggestRepository


class SearchSuggestPgRepository(SearchSuggestRepository):
    async def introduce_myself(self, query: SearchSuggestQuery) -> SearchSuggestResponse:
        return SearchSuggestResponse(id=query.id, name=query.name)
