from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.restaurant_location_schema import RestaurantLocationSchema
from restaurant.app.dtos.restaurant_location_dto import RestaurantLocationResponse


class RestaurantLocationUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: RestaurantLocationSchema) -> RestaurantLocationResponse:
        pass
