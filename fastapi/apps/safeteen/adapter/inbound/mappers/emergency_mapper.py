from __future__ import annotations

from safeteen.adapter.inbound.api.schemas.emergency_schema import (
    EmergencyGuideResponse,
    EmergencyHotlineResponse,
    EmergencyStepResponse,
)
from safeteen.app.dtos.emergency_dto import EmergencyGuideResult


def to_response(result: EmergencyGuideResult) -> EmergencyGuideResponse:
    return EmergencyGuideResponse(
        account_freeze_steps=[
            EmergencyStepResponse(order=step.order, title=step.title, description=step.description)
            for step in result.account_freeze_steps
        ],
        police_report_steps=[
            EmergencyStepResponse(order=step.order, title=step.title, description=step.description)
            for step in result.police_report_steps
        ],
        hotlines=[
            EmergencyHotlineResponse(
                name=hotline.name, phone_number=hotline.phone_number, description=hotline.description
            )
            for hotline in result.hotlines
        ],
    )
