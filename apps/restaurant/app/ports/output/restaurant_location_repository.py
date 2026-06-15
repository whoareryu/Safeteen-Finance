from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.restaurant_location_dto import RestaurantLocationQuery, RestaurantLocationResponse


class RestaurantLocationRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: RestaurantLocationQuery) -> RestaurantLocationResponse:
        pass
