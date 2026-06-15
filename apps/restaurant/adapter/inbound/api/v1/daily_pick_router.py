from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.daily_pick_schema import DailyPickSchema
from restaurant.app.dtos.daily_pick_dto import DailyPickResponse
from restaurant.app.ports.input.daily_pick_use_case import DailyPickUseCase
from restaurant.dependencies.daily_pick_provider import get_daily_pick_use_case

daily_pick_router = APIRouter(prefix="/gourmet", tags=["gourmet-daily_pick"])
router = daily_pick_router


@daily_pick_router.get("/myself")
async def introduce_myself(
    use_case: DailyPickUseCase = Depends(get_daily_pick_use_case),
) -> DailyPickResponse:
    return await use_case.introduce_myself(DailyPickSchema(id=1, name="오늘의 맛집 추천"))
