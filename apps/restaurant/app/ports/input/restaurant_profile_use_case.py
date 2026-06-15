from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.restaurant_profile_schema import RestaurantProfileSchema
from restaurant.app.dtos.restaurant_profile_dto import RestaurantProfileResponse


class RestaurantProfileUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: RestaurantProfileSchema) -> RestaurantProfileResponse:
        pass
