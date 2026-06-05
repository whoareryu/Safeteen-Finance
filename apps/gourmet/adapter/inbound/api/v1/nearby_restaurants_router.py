"""nearby_restaurants API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

nearby_restaurants_router = APIRouter(prefix="/gourmet", tags=["gourmet-nearby_restaurants"])
router = nearby_restaurants_router
