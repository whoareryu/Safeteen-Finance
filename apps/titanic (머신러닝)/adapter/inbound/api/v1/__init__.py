from fastapi import APIRouter

from apps.titanic.adapter.inbound.api.v1.james_router import james_router
from apps.titanic.adapter.inbound.api.v1.walter_router import router as walter_router

router = APIRouter(prefix="/titanic")
router.include_router(james_router)
router.include_router(walter_router)

__all__ = ["router"]
