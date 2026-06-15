from __future__ import annotations

from restaurant.app.dtos.search_query_dto import SearchQueryQuery, SearchQueryResponse
from restaurant.app.ports.output.search_query_repository import SearchQueryRepository


class SearchQueryPgRepository(SearchQueryRepository):
    async def introduce_myself(self, query: SearchQueryQuery) -> SearchQueryResponse:
        return SearchQueryResponse(id=query.id, name=query.name)
