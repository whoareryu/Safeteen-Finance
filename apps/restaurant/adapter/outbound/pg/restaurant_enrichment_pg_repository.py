from __future__ import annotations

from restaurant.app.dtos.restaurant_enrichment_dto import RestaurantEnrichmentQuery, RestaurantEnrichmentResponse
from restaurant.app.ports.output.restaurant_enrichment_repository import RestaurantEnrichmentRepository


class RestaurantEnrichmentPgRepository(RestaurantEnrichmentRepository):
    async def introduce_myself(self, query: RestaurantEnrichmentQuery) -> RestaurantEnrichmentResponse:
        return RestaurantEnrichmentResponse(id=query.id, name=query.name)
