"""restaurant_location API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

restaurant_location_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_location"])
router = restaurant_location_router
