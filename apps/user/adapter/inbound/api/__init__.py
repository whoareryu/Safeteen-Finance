from fastapi import APIRouter

from user.adapter.inbound.api.v1.onboarding_router import onboarding_router
from user.adapter.inbound.api.v1.budget_report_router import budget_report_router
from user.adapter.inbound.api.v1.visit_rating_router import visit_rating_router

user_router = APIRouter()
user_router.include_router(onboarding_router)
user_router.include_router(budget_report_router)
user_router.include_router(visit_rating_router)

router = user_router

__all__ = ["user_router", "router"]
