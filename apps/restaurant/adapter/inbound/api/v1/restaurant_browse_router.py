from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.restaurant_browse_schema import RestaurantBrowseSchema
from restaurant.app.dtos.restaurant_browse_dto import RestaurantBrowseResponse
from restaurant.app.ports.input.restaurant_browse_use_case import RestaurantBrowseUseCase
from restaurant.dependencies.restaurant_browse_provider import get_restaurant_browse_use_case

restaurant_browse_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_browse"])
router = restaurant_browse_router


@restaurant_browse_router.get("/myself")
async def introduce_myself(
    use_case: RestaurantBrowseUseCase = Depends(get_restaurant_browse_use_case),
) -> RestaurantBrowseResponse:
    return await use_case.introduce_myself(RestaurantBrowseSchema(id=1, name="맛집 탐색"))
