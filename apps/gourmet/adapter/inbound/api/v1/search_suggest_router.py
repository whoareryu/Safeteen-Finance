"""search_suggest API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

search_suggest_router = APIRouter(prefix="/gourmet", tags=["gourmet-search_suggest"])
router = search_suggest_router
