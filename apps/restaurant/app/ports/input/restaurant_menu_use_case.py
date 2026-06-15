from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.restaurant_menu_schema import RestaurantMenuSchema
from restaurant.app.dtos.restaurant_menu_dto import RestaurantMenuResponse


class RestaurantMenuUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: RestaurantMenuSchema) -> RestaurantMenuResponse:
        pass
