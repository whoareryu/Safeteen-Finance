"""view_stat API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

view_stat_router = APIRouter(prefix="/gourmet", tags=["gourmet-view_stat"])
router = view_stat_router
