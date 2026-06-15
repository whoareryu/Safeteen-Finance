from __future__ import annotations

from restaurant.app.dtos.restaurant_menu_dto import RestaurantMenuQuery, RestaurantMenuResponse
from restaurant.app.ports.output.restaurant_menu_repository import RestaurantMenuRepository


class RestaurantMenuPgRepository(RestaurantMenuRepository):
    async def introduce_myself(self, query: RestaurantMenuQuery) -> RestaurantMenuResponse:
        return RestaurantMenuResponse(id=query.id, name=query.name)
