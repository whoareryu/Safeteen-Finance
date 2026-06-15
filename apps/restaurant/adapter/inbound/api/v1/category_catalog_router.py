from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.category_catalog_schema import CategoryCatalogSchema
from restaurant.app.dtos.category_catalog_dto import CategoryCatalogResponse
from restaurant.app.ports.input.category_catalog_use_case import CategoryCatalogUseCase
from restaurant.dependencies.category_catalog_provider import get_category_catalog_use_case

category_catalog_router = APIRouter(prefix="/gourmet", tags=["gourmet-category_catalog"])
router = category_catalog_router


@category_catalog_router.get("/myself")
async def introduce_myself(
    use_case: CategoryCatalogUseCase = Depends(get_category_catalog_use_case),
) -> CategoryCatalogResponse:
    return await use_case.introduce_myself(CategoryCatalogSchema(id=1, name="카테고리 카탈로그"))
