from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.restaurant_menu_dto import RestaurantMenuQuery, RestaurantMenuResponse


class RestaurantMenuRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: RestaurantMenuQuery) -> RestaurantMenuResponse:
        pass
