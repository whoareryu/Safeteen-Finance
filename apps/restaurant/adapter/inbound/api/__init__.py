from fastapi import APIRouter

from restaurant.adapter.inbound.api.v1.admin_router import router as admin_router
from restaurant.adapter.inbound.api.v1.gourmet_chat_router import router as gourmet_chat_router
from restaurant.adapter.inbound.api.v1.gourmet_router import router as gourmet_legacy_router
from restaurant.adapter.inbound.api.v1.weather_router import router as weather_router

from restaurant.adapter.inbound.api.v1.course_recommendation_router import course_recommendation_router
from restaurant.adapter.inbound.api.v1.diet_recommendation_router import diet_recommendation_router
from restaurant.adapter.inbound.api.v1.personalized_recommendation_router import personalized_recommendation_router

restaurant_router = APIRouter()
restaurant_router.include_router(gourmet_chat_router)
restaurant_router.include_router(gourmet_legacy_router)
restaurant_router.include_router(admin_router)
restaurant_router.include_router(weather_router)

restaurant_router.include_router(course_recommendation_router)
restaurant_router.include_router(diet_recommendation_router)
restaurant_router.include_router(personalized_recommendation_router)

router = restaurant_router

__all__ = ["restaurant_router", "router"]
