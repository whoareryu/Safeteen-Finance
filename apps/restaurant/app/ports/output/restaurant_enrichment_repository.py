from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.app.dtos.restaurant_enrichment_dto import RestaurantEnrichmentQuery, RestaurantEnrichmentResponse


class RestaurantEnrichmentRepository(ABC):
    @abstractmethod
    async def introduce_myself(self, query: RestaurantEnrichmentQuery) -> RestaurantEnrichmentResponse:
        pass
