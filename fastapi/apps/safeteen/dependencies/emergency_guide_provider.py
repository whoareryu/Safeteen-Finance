from __future__ import annotations

from safeteen.adapter.outbound.memory.static_emergency_guide_repository import (
    StaticEmergencyGuideRepository,
)
from safeteen.app.ports.input.emergency_guide_use_case import EmergencyGuideUseCase
from safeteen.app.use_cases.emergency_guide_interactor import EmergencyGuideInteractor


def get_emergency_guide_use_case() -> EmergencyGuideUseCase:
    return EmergencyGuideInteractor(repository=StaticEmergencyGuideRepository())
