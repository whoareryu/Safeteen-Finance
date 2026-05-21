from fastapi import APIRouter

from apps.gourmet.app.controllers.gourmet_router import router as gourmet_legacy_router
from apps.gourmet.app.controllers.meal_plan_router import router as meal_plan_router
from apps.gourmet.app.controllers.restaurant_router import router as restaurant_v2_router

router = APIRouter()
router.include_router(gourmet_legacy_router)
router.include_router(meal_plan_router)
router.include_router(restaurant_v2_router)

__all__ = ["router"]
