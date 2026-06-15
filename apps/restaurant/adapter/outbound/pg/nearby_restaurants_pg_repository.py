from __future__ import annotations

from restaurant.app.dtos.nearby_restaurants_dto import NearbyRestaurantsQuery, NearbyRestaurantsResponse
from restaurant.app.ports.output.nearby_restaurants_repository import NearbyRestaurantsRepository


class NearbyRestaurantsPgRepository(NearbyRestaurantsRepository):
    async def introduce_myself(self, query: NearbyRestaurantsQuery) -> NearbyRestaurantsResponse:
        return NearbyRestaurantsResponse(id=query.id, name=query.name)
