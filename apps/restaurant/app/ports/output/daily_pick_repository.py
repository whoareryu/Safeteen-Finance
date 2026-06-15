from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.daily_pick_dto import DailyPickQuery, DailyPickResponse


class DailyPickRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: DailyPickQuery) -> DailyPickResponse:
        pass
