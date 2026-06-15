from __future__ import annotations

from abc import ABC, abstractmethod

from restaurant.adapter.inbound.api.schemas.restaurant_enrichment_schema import RestaurantEnrichmentSchema
from restaurant.app.dtos.restaurant_enrichment_dto import RestaurantEnrichmentResponse


class RestaurantEnrichmentUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: RestaurantEnrichmentSchema) -> RestaurantEnrichmentResponse:
        pass
