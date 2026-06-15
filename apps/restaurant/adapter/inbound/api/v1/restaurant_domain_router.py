from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.restaurant_domain_schema import RestaurantDomainSchema
from restaurant.app.dtos.restaurant_domain_dto import RestaurantDomainResponse
from restaurant.app.ports.input.restaurant_domain_use_case import RestaurantDomainUseCase
from restaurant.dependencies.restaurant_domain_provider import get_restaurant_domain_use_case

restaurant_domain_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_domain"])
router = restaurant_domain_router


@restaurant_domain_router.get("/myself")
async def introduce_myself(
    use_case: RestaurantDomainUseCase = Depends(get_restaurant_domain_use_case),
) -> RestaurantDomainResponse:
    return await use_case.introduce_myself(RestaurantDomainSchema(id=1, name="맛집 도메인"))
