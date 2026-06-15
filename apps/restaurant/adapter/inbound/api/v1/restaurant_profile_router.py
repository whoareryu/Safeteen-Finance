from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.restaurant_profile_schema import RestaurantProfileSchema
from restaurant.app.dtos.restaurant_profile_dto import RestaurantProfileResponse
from restaurant.app.ports.input.restaurant_profile_use_case import RestaurantProfileUseCase
from restaurant.dependencies.restaurant_profile_provider import get_restaurant_profile_use_case

restaurant_profile_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_profile"])
router = restaurant_profile_router


@restaurant_profile_router.get("/myself")
async def introduce_myself(
    use_case: RestaurantProfileUseCase = Depends(get_restaurant_profile_use_case),
) -> RestaurantProfileResponse:
    return await use_case.introduce_myself(RestaurantProfileSchema(id=1, name="맛집 프로필"))
