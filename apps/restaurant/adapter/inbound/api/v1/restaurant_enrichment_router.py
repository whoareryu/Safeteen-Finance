from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.restaurant_enrichment_schema import RestaurantEnrichmentSchema
from restaurant.app.dtos.restaurant_enrichment_dto import RestaurantEnrichmentResponse
from restaurant.app.ports.input.restaurant_enrichment_use_case import RestaurantEnrichmentUseCase
from restaurant.dependencies.restaurant_enrichment_provider import get_restaurant_enrichment_use_case

restaurant_enrichment_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_enrichment"])
router = restaurant_enrichment_router


@restaurant_enrichment_router.get("/myself")
async def introduce_myself(
    use_case: RestaurantEnrichmentUseCase = Depends(get_restaurant_enrichment_use_case),
) -> RestaurantEnrichmentResponse:
    return await use_case.introduce_myself(RestaurantEnrichmentSchema(id=1, name="맛집 보강"))
