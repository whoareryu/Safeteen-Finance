"""category_browse API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

category_browse_router = APIRouter(prefix="/gourmet", tags=["gourmet-category_browse"])
router = category_browse_router
