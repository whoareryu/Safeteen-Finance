from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.restaurant_browse_schema import RestaurantBrowseSchema
from restaurant.app.dtos.restaurant_browse_dto import RestaurantBrowseResponse


class RestaurantBrowseUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: RestaurantBrowseSchema) -> RestaurantBrowseResponse:
        pass
