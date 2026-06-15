from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.restaurant_profile_dto import RestaurantProfileQuery, RestaurantProfileResponse


class RestaurantProfileRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: RestaurantProfileQuery) -> RestaurantProfileResponse:
        pass
