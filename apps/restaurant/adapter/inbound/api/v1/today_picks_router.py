from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.today_picks_schema import TodayPicksSchema
from restaurant.app.dtos.today_picks_dto import TodayPicksResponse
from restaurant.app.ports.input.today_picks_use_case import TodayPicksUseCase
from restaurant.dependencies.today_picks_provider import get_today_picks_use_case

today_picks_router = APIRouter(prefix="/gourmet", tags=["gourmet-today_picks"])
router = today_picks_router


@today_picks_router.get("/myself")
async def introduce_myself(
    use_case: TodayPicksUseCase = Depends(get_today_picks_use_case),
) -> TodayPicksResponse:
    return await use_case.introduce_myself(TodayPicksSchema(id=1, name="오늘의 추천 목록"))
