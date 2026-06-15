from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.restaurant_detail_dto import RestaurantDetailQuery, RestaurantDetailResponse


class RestaurantDetailRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: RestaurantDetailQuery) -> RestaurantDetailResponse:
        pass
