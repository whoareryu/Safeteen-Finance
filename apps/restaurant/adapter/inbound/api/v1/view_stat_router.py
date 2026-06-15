from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.view_stat_schema import ViewStatSchema
from restaurant.app.dtos.view_stat_dto import ViewStatResponse
from restaurant.app.ports.input.view_stat_use_case import ViewStatUseCase
from restaurant.dependencies.view_stat_provider import get_view_stat_use_case

view_stat_router = APIRouter(prefix="/gourmet", tags=["gourmet-view_stat"])
router = view_stat_router


@view_stat_router.get("/myself")
async def introduce_myself(
    use_case: ViewStatUseCase = Depends(get_view_stat_use_case),
) -> ViewStatResponse:
    return await use_case.introduce_myself(ViewStatSchema(id=1, name="조회수 집계"))
