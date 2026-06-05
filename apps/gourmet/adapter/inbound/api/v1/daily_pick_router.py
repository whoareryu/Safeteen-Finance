"""daily_pick API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

daily_pick_router = APIRouter(prefix="/gourmet", tags=["gourmet-daily_pick"])
router = daily_pick_router
