from __future__ import annotations

from restaurant.app.dtos.restaurant_browse_dto import RestaurantBrowseQuery, RestaurantBrowseResponse
from restaurant.app.ports.output.restaurant_browse_repository import RestaurantBrowseRepository


class RestaurantBrowsePgRepository(RestaurantBrowseRepository):
    async def introduce_myself(self, query: RestaurantBrowseQuery) -> RestaurantBrowseResponse:
        return RestaurantBrowseResponse(id=query.id, name=query.name)
