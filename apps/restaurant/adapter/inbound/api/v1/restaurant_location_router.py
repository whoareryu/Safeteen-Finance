from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.restaurant_location_schema import RestaurantLocationSchema
from restaurant.app.dtos.restaurant_location_dto import RestaurantLocationResponse
from restaurant.app.ports.input.restaurant_location_use_case import RestaurantLocationUseCase
from restaurant.dependencies.restaurant_location_provider import get_restaurant_location_use_case

restaurant_location_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_location"])
router = restaurant_location_router


@restaurant_location_router.get("/myself")
async def introduce_myself(
    use_case: RestaurantLocationUseCase = Depends(get_restaurant_location_use_case),
) -> RestaurantLocationResponse:
    return await use_case.introduce_myself(RestaurantLocationSchema(id=1, name="맛집 위치"))
