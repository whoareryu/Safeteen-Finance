"""restaurant_menu API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

restaurant_menu_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_menu"])
router = restaurant_menu_router
