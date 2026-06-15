from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.nearby_restaurants_schema import NearbyRestaurantsSchema
from restaurant.app.dtos.nearby_restaurants_dto import NearbyRestaurantsResponse
from restaurant.app.ports.input.nearby_restaurants_use_case import NearbyRestaurantsUseCase
from restaurant.dependencies.nearby_restaurants_provider import get_nearby_restaurants_use_case

nearby_restaurants_router = APIRouter(prefix="/gourmet", tags=["gourmet-nearby_restaurants"])
router = nearby_restaurants_router


@nearby_restaurants_router.get("/myself")
async def introduce_myself(
    use_case: NearbyRestaurantsUseCase = Depends(get_nearby_restaurants_use_case),
) -> NearbyRestaurantsResponse:
    return await use_case.introduce_myself(NearbyRestaurantsSchema(id=1, name="근처 맛집"))
