"""topic_restaurants API — endpoints는 gourmet_router/catalog_router에서 점진 분리."""

from fastapi import APIRouter

topic_restaurants_router = APIRouter(prefix="/gourmet", tags=["gourmet-topic_restaurants"])
router = topic_restaurants_router
