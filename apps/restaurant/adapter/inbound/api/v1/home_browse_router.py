from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.home_browse_schema import HomeBrowseSchema
from restaurant.app.dtos.home_browse_dto import HomeBrowseResponse
from restaurant.app.ports.input.home_browse_use_case import HomeBrowseUseCase
from restaurant.dependencies.home_browse_provider import get_home_browse_use_case

home_browse_router = APIRouter(prefix="/gourmet", tags=["gourmet-home_browse"])
router = home_browse_router


@home_browse_router.get("/myself")
async def introduce_myself(
    use_case: HomeBrowseUseCase = Depends(get_home_browse_use_case),
) -> HomeBrowseResponse:
    return await use_case.introduce_myself(HomeBrowseSchema(id=1, name="홈 피드"))
