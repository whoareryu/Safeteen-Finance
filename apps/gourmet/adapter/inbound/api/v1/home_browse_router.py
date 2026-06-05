"""home_browse API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

home_browse_router = APIRouter(prefix="/gourmet", tags=["gourmet-home_browse"])
router = home_browse_router
