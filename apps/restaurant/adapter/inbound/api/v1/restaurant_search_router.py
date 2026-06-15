from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.restaurant_search_schema import RestaurantSearchSchema
from restaurant.app.dtos.restaurant_search_dto import RestaurantSearchResponse
from restaurant.app.ports.input.restaurant_search_use_case import RestaurantSearchUseCase
from restaurant.dependencies.restaurant_search_provider import get_restaurant_search_use_case

restaurant_search_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_search"])
router = restaurant_search_router


@restaurant_search_router.get("/myself")
async def introduce_myself(
    use_case: RestaurantSearchUseCase = Depends(get_restaurant_search_use_case),
) -> RestaurantSearchResponse:
    return await use_case.introduce_myself(RestaurantSearchSchema(id=1, name="맛집 검색"))
