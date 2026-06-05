"""category_catalog API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

category_catalog_router = APIRouter(prefix="/gourmet", tags=["gourmet-category_catalog"])
router = category_catalog_router
