from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.restaurant_menu_schema import RestaurantMenuSchema
from restaurant.app.dtos.restaurant_menu_dto import RestaurantMenuResponse
from restaurant.app.ports.input.restaurant_menu_use_case import RestaurantMenuUseCase
from restaurant.dependencies.restaurant_menu_provider import get_restaurant_menu_use_case

restaurant_menu_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_menu"])
router = restaurant_menu_router


@restaurant_menu_router.get("/myself")
async def introduce_myself(
    use_case: RestaurantMenuUseCase = Depends(get_restaurant_menu_use_case),
) -> RestaurantMenuResponse:
    return await use_case.introduce_myself(RestaurantMenuSchema(id=1, name="맛집 메뉴"))
