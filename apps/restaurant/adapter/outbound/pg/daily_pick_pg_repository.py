from __future__ import annotations

from restaurant.app.dtos.daily_pick_dto import DailyPickQuery, DailyPickResponse
from restaurant.app.ports.output.daily_pick_repository import DailyPickRepository


class DailyPickPgRepository(DailyPickRepository):
    async def introduce_myself(self, query: DailyPickQuery) -> DailyPickResponse:
        return DailyPickResponse(id=query.id, name=query.name)
