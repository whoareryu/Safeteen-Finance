from __future__ import annotations

from restaurant.app.dtos.today_picks_dto import TodayPicksQuery, TodayPicksResponse
from restaurant.app.ports.output.today_picks_repository import TodayPicksRepository


class TodayPicksPgRepository(TodayPicksRepository):
    async def introduce_myself(self, query: TodayPicksQuery) -> TodayPicksResponse:
        return TodayPicksResponse(id=query.id, name=query.name)
