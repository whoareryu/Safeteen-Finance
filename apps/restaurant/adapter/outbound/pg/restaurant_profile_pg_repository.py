from __future__ import annotations

from restaurant.app.dtos.restaurant_profile_dto import RestaurantProfileQuery, RestaurantProfileResponse
from restaurant.app.ports.output.restaurant_profile_repository import RestaurantProfileRepository


class RestaurantProfilePgRepository(RestaurantProfileRepository):
    async def introduce_myself(self, query: RestaurantProfileQuery) -> RestaurantProfileResponse:
        return RestaurantProfileResponse(id=query.id, name=query.name)
