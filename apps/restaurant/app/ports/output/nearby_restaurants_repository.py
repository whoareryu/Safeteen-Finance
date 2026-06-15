from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.nearby_restaurants_dto import NearbyRestaurantsQuery, NearbyRestaurantsResponse


class NearbyRestaurantsRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: NearbyRestaurantsQuery) -> NearbyRestaurantsResponse:
        pass
