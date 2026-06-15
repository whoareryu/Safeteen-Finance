from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.today_picks_dto import TodayPicksQuery, TodayPicksResponse


class TodayPicksRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: TodayPicksQuery) -> TodayPicksResponse:
        pass
