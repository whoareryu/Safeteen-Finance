from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.view_stat_schema import ViewStatSchema
from restaurant.app.dtos.view_stat_dto import ViewStatResponse


class ViewStatUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: ViewStatSchema) -> ViewStatResponse:
        pass
