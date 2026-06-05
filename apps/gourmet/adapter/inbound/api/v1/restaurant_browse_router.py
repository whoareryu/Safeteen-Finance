"""restaurant_browse API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

restaurant_browse_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_browse"])
router = restaurant_browse_router
