"""restaurant_profile API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

restaurant_profile_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_profile"])
router = restaurant_profile_router
