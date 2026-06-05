"""restaurant_domain API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

restaurant_domain_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_domain"])
router = restaurant_domain_router
