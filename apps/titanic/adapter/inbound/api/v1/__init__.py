from fastapi import APIRouter

from apps.titanic.adapter.inbound.api.v1.titanic_command_router import (
    router as titanic_command_router,
)
from apps.titanic.adapter.inbound.api.v1.titanic_query_router import (
    router as titanic_query_router,
)

router = APIRouter(prefix="/titanic")
router.include_router(titanic_query_router)
router.include_router(titanic_command_router)

__all__ = ["router"]
