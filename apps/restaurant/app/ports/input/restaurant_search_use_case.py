from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.restaurant_search_schema import RestaurantSearchSchema
from restaurant.app.dtos.restaurant_search_dto import RestaurantSearchResponse


class RestaurantSearchUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: RestaurantSearchSchema) -> RestaurantSearchResponse:
        pass
