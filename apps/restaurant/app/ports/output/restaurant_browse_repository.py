from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.restaurant_browse_dto import RestaurantBrowseQuery, RestaurantBrowseResponse


class RestaurantBrowseRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: RestaurantBrowseQuery) -> RestaurantBrowseResponse:
        pass
