from __future__ import annotations

from fastapi import APIRouter, Depends

from plant.adapter.inbound.mappers.care_guide_mapper import to_response
from plant.adapter.inbound.api.schemas.care_guide_schema import CareGuideResponse
from plant.app.dtos.care_guide_dto import CareGuideCommand
from plant.app.ports.input.care_guide_use_case import CareGuideUseCase
from plant.dependencies.care_guide_provider import get_care_guide_use_case

care_guide_router = APIRouter(tags=["plant-care-guide"])


@care_guide_router.post("/diagnosis/{diagnosis_id}/care-guide", summary="진단 결과 → 케어 처방 생성")
async def generate_care_guide(
    diagnosis_id: int,
    use_case: CareGuideUseCase = Depends(get_care_guide_use_case),
) -> CareGuideResponse:
    result = await use_case.generate(CareGuideCommand(diagnosis_id=diagnosis_id))
    return to_response(result)
