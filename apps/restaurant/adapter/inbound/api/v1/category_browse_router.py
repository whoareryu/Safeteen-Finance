from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.category_browse_schema import CategoryBrowseSchema
from restaurant.app.dtos.category_browse_dto import CategoryBrowseResponse
from restaurant.app.ports.input.category_browse_use_case import CategoryBrowseUseCase
from restaurant.dependencies.category_browse_provider import get_category_browse_use_case

category_browse_router = APIRouter(prefix="/gourmet", tags=["gourmet-category_browse"])
router = category_browse_router


@category_browse_router.get("/myself")
async def introduce_myself(
    use_case: CategoryBrowseUseCase = Depends(get_category_browse_use_case),
) -> CategoryBrowseResponse:
    return await use_case.introduce_myself(CategoryBrowseSchema(id=1, name="카테고리 탐색"))
