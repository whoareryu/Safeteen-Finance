"""search_query API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

search_query_router = APIRouter(prefix="/gourmet", tags=["gourmet-search_query"])
router = search_query_router
