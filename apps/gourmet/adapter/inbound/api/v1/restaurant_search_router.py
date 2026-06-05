"""restaurant_search API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

restaurant_search_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_search"])
router = restaurant_search_router
