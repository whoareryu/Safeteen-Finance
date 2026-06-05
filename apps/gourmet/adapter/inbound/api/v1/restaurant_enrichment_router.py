"""restaurant_enrichment API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

restaurant_enrichment_router = APIRouter(prefix="/gourmet", tags=["gourmet-restaurant_enrichment"])
router = restaurant_enrichment_router
