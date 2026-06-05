"""restaurant_detail API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

restaurant_detail_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_detail"])
router = restaurant_detail_router
