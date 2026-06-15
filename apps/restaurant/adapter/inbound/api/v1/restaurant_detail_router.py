from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.restaurant_detail_schema import RestaurantDetailSchema
from restaurant.app.dtos.restaurant_detail_dto import RestaurantDetailResponse
from restaurant.app.ports.input.restaurant_detail_use_case import RestaurantDetailUseCase
from restaurant.dependencies.restaurant_detail_provider import get_restaurant_detail_use_case

restaurant_detail_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_detail"])
router = restaurant_detail_router


@restaurant_detail_router.get("/myself")
async def introduce_myself(
    use_case: RestaurantDetailUseCase = Depends(get_restaurant_detail_use_case),
) -> RestaurantDetailResponse:
    return await use_case.introduce_myself(RestaurantDetailSchema(id=1, name="맛집 상세"))
