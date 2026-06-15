from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.restaurant_search_dto import RestaurantSearchQuery, RestaurantSearchResponse


class RestaurantSearchRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: RestaurantSearchQuery) -> RestaurantSearchResponse:
        pass
