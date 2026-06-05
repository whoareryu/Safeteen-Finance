"""today_picks API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

today_picks_router = APIRouter(prefix="/gourmet", tags=["gourmet-today_picks"])
router = today_picks_router
