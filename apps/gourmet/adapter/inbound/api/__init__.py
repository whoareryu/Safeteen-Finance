from fastapi import APIRouter

from gourmet.adapter.inbound.api.v1.admin_router import router as admin_router
from gourmet.adapter.inbound.api.v1.catalog_router import router as catalog_router
from gourmet.adapter.inbound.api.v1.favorite_router import favorite_router
from gourmet.adapter.inbound.api.v1.gourmet_chat_router import router as gourmet_chat_router
from gourmet.adapter.inbound.api.v1.gourmet_router import router as gourmet_legacy_router
from gourmet.adapter.inbound.api.v1.meal_plan_router import router as meal_plan_router
from gourmet.adapter.inbound.api.v1.restaurant_router import router as restaurant_v2_router
from gourmet.adapter.inbound.api.v1.weather_router import router as weather_router

# feature slice routers (엔드포인트 점진 분리 — 현재는 legacy/catalog 가 본체)
from gourmet.adapter.inbound.api.v1 import (  # noqa: F401
    category_browse_router,
    category_catalog_router,
    daily_pick_router,
    home_browse_router,
    nearby_restaurants_router,
    restaurant_detail_router,
    restaurant_search_router,
    search_suggest_router,
    today_picks_router,
    topic_restaurants_router,
)

gourmet_router = APIRouter()
gourmet_router.include_router(catalog_router)
gourmet_router.include_router(gourmet_chat_router)
gourmet_router.include_router(gourmet_legacy_router)
gourmet_router.include_router(meal_plan_router)
gourmet_router.include_router(restaurant_v2_router)
gourmet_router.include_router(admin_router)
gourmet_router.include_router(favorite_router)
gourmet_router.include_router(weather_router)

router = gourmet_router

__all__ = ["gourmet_router", "router"]
