from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.home_browse_schema import HomeBrowseSchema
from restaurant.app.dtos.home_browse_dto import HomeBrowseResponse


class HomeBrowseUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: HomeBrowseSchema) -> HomeBrowseResponse:
        pass
