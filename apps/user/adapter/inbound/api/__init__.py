from fastapi import APIRouter

from user.adapter.inbound.api.v1.favorite_router import favorite_router
from user.adapter.inbound.api.v1.meal_plan_router import router as meal_plan_router

user_router = APIRouter()
user_router.include_router(favorite_router)
user_router.include_router(meal_plan_router)

router = user_router

__all__ = ["user_router", "router"]
