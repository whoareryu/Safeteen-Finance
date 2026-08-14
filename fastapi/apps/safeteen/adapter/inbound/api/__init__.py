from fastapi import APIRouter

from safeteen.adapter.inbound.api.v1.analysis_router import analysis_router
from safeteen.adapter.inbound.api.v1.emergency_router import emergency_router
from safeteen.adapter.inbound.api.v1.incident_report_router import incident_report_router
from safeteen.adapter.inbound.api.v1.policy_router import policy_router

safeteen_router = APIRouter(prefix="/safeteen", tags=["safeteen"])
safeteen_router.include_router(analysis_router)
safeteen_router.include_router(policy_router)
safeteen_router.include_router(emergency_router)
safeteen_router.include_router(incident_report_router)

__all__ = ["safeteen_router"]
