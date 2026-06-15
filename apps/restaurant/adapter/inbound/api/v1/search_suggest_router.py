from fastapi import APIRouter, Depends

from restaurant.adapter.inbound.api.schemas.search_suggest_schema import SearchSuggestSchema
from restaurant.app.dtos.search_suggest_dto import SearchSuggestResponse
from restaurant.app.ports.input.search_suggest_use_case import SearchSuggestUseCase
from restaurant.dependencies.search_suggest_provider import get_search_suggest_use_case

search_suggest_router = APIRouter(prefix="/gourmet", tags=["gourmet-search_suggest"])
router = search_suggest_router


@search_suggest_router.get("/myself")
async def introduce_myself(
    use_case: SearchSuggestUseCase = Depends(get_search_suggest_use_case),
) -> SearchSuggestResponse:
    return await use_case.introduce_myself(SearchSuggestSchema(id=1, name="검색 제안"))
