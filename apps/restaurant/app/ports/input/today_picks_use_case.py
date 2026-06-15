from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.today_picks_schema import TodayPicksSchema
from restaurant.app.dtos.today_picks_dto import TodayPicksResponse


class TodayPicksUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: TodayPicksSchema) -> TodayPicksResponse:
        pass
