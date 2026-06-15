from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.nearby_restaurants_schema import NearbyRestaurantsSchema
from restaurant.app.dtos.nearby_restaurants_dto import NearbyRestaurantsResponse


class NearbyRestaurantsUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: NearbyRestaurantsSchema) -> NearbyRestaurantsResponse:
        pass
