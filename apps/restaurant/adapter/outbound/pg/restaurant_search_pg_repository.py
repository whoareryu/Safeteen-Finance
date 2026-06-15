from __future__ import annotations

from restaurant.app.dtos.restaurant_search_dto import RestaurantSearchQuery, RestaurantSearchResponse
from restaurant.app.ports.output.restaurant_search_repository import RestaurantSearchRepository


class RestaurantSearchPgRepository(RestaurantSearchRepository):
    async def introduce_myself(self, query: RestaurantSearchQuery) -> RestaurantSearchResponse:
        return RestaurantSearchResponse(id=query.id, name=query.name)
