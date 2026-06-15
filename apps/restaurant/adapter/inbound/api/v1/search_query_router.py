from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.search_query_schema import SearchQuerySchema
from restaurant.app.dtos.search_query_dto import SearchQueryResponse
from restaurant.app.ports.input.search_query_use_case import SearchQueryUseCase
from restaurant.dependencies.search_query_provider import get_search_query_use_case

search_query_router = APIRouter(prefix="/gourmet", tags=["gourmet-search_query"])
router = search_query_router


@search_query_router.get("/myself")
async def introduce_myself(
    use_case: SearchQueryUseCase = Depends(get_search_query_use_case),
) -> SearchQueryResponse:
    return await use_case.introduce_myself(SearchQuerySchema(id=1, name="검색 쿼리"))
