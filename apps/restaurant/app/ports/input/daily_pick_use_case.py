from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.daily_pick_schema import DailyPickSchema
from restaurant.app.dtos.daily_pick_dto import DailyPickResponse


class DailyPickUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: DailyPickSchema) -> DailyPickResponse:
        pass
