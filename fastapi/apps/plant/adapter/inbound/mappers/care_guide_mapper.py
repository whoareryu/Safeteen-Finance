from __future__ import annotations

from plant.adapter.inbound.api.schemas.care_guide_schema import CareGuideResponse
from plant.app.dtos.care_guide_dto import CareGuideResult


def to_response(result: CareGuideResult) -> CareGuideResponse:
    return CareGuideResponse(
        id=result.id,
        diagnosis_record_id=result.diagnosis_record_id,
        prescription_text=result.prescription_text,
    )
