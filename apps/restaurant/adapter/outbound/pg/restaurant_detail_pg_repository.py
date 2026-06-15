from __future__ import annotations

from restaurant.app.dtos.restaurant_detail_dto import RestaurantDetailQuery, RestaurantDetailResponse
from restaurant.app.ports.output.restaurant_detail_repository import RestaurantDetailRepository


class RestaurantDetailPgRepository(RestaurantDetailRepository):
    async def introduce_myself(self, query: RestaurantDetailQuery) -> RestaurantDetailResponse:
        return RestaurantDetailResponse(id=query.id, name=query.name)
