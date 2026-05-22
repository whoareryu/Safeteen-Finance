from fastapi import APIRouter

from apps.gourmet.app.controllers.admin_router import router as admin_router
from apps.gourmet.app.controllers.catalog_router import router as catalog_router
from apps.gourmet.app.controllers.favorite_router import router as favorite_router
from apps.gourmet.app.controllers.gourmet_chat_router import router as gourmet_chat_router
from apps.gourmet.app.controllers.gourmet_router import router as gourmet_legacy_router
from apps.gourmet.app.controllers.meal_plan_router import router as meal_plan_router
from apps.gourmet.app.controllers.restaurant_router import router as restaurant_v2_router

router = APIRouter()
router.include_router(catalog_router)
router.include_router(gourmet_chat_router)
router.include_router(gourmet_legacy_router)
router.include_router(meal_plan_router)
router.include_router(restaurant_v2_router)
router.include_router(admin_router)
router.include_router(favorite_router)

__all__ = ["router"]
