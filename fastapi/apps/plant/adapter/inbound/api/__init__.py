from fastapi import APIRouter

from plant.adapter.inbound.api.v1.care_guide_router import care_guide_router
from plant.adapter.inbound.api.v1.chat_router import chat_router
from plant.adapter.inbound.api.v1.diagnosis_router import diagnosis_router
from plant.adapter.inbound.api.v1.knowledge_sync_router import knowledge_sync_router
from plant.adapter.inbound.api.v1.my_plants_router import my_plants_router
from plant.adapter.inbound.api.v1.notification_router import notification_router
from plant.adapter.inbound.api.v1.weather_router import weather_router

plant_router = APIRouter(prefix="/plant", tags=["plant"])
plant_router.include_router(diagnosis_router)
plant_router.include_router(care_guide_router)
plant_router.include_router(chat_router)
plant_router.include_router(my_plants_router)
plant_router.include_router(weather_router)
plant_router.include_router(notification_router)
plant_router.include_router(knowledge_sync_router)

__all__ = [
    "plant_router",
    "diagnosis_router",
    "care_guide_router",
    "chat_router",
    "my_plants_router",
    "weather_router",
    "notification_router",
    "knowledge_sync_router",
]
