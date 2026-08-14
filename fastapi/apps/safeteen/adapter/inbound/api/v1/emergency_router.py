from __future__ import annotations

from fastapi import APIRouter, Depends

from safeteen.adapter.inbound.api.schemas.emergency_schema import (
    EmergencyGuideRequest,
    EmergencyGuideResponse,
)
from safeteen.adapter.inbound.mappers.emergency_mapper import to_response
from safeteen.app.dtos.emergency_dto import EmergencyGuideCommand
from safeteen.app.ports.input.emergency_guide_use_case import EmergencyGuideUseCase
from safeteen.dependencies.emergency_guide_provider import get_emergency_guide_use_case

emergency_router = APIRouter(tags=["safeteen-emergency"])


@emergency_router.post("/emergency-guide", summary="계좌 도용/사기 피해 즉각 대응 가이드 조회")
def get_emergency_guide(
    body: EmergencyGuideRequest,
    use_case: EmergencyGuideUseCase = Depends(get_emergency_guide_use_case),
) -> EmergencyGuideResponse:
    result = use_case.get_guide(EmergencyGuideCommand(situation=body.situation))
    return to_response(result)
