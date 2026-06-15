from __future__ import annotations

from restaurant.app.dtos.home_browse_dto import HomeBrowseQuery, HomeBrowseResponse
from restaurant.app.ports.output.home_browse_repository import HomeBrowseRepository


class HomeBrowsePgRepository(HomeBrowseRepository):
    async def introduce_myself(self, query: HomeBrowseQuery) -> HomeBrowseResponse:
        return HomeBrowseResponse(id=query.id, name=query.name)
