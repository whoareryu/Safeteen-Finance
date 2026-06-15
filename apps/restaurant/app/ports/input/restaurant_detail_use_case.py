from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.restaurant_detail_schema import RestaurantDetailSchema
from restaurant.app.dtos.restaurant_detail_dto import RestaurantDetailResponse


class RestaurantDetailUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: RestaurantDetailSchema) -> RestaurantDetailResponse:
        pass
