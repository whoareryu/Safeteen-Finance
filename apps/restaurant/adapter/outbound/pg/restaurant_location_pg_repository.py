from __future__ import annotations

from restaurant.app.dtos.restaurant_location_dto import RestaurantLocationQuery, RestaurantLocationResponse
from restaurant.app.ports.output.restaurant_location_repository import RestaurantLocationRepository


class RestaurantLocationPgRepository(RestaurantLocationRepository):
    async def introduce_myself(self, query: RestaurantLocationQuery) -> RestaurantLocationResponse:
        return RestaurantLocationResponse(id=query.id, name=query.name)
