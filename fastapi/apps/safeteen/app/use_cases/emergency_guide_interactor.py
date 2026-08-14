from __future__ import annotations

from safeteen.app.dtos.emergency_dto import EmergencyGuideCommand, EmergencyGuideResult
from safeteen.app.ports.input.emergency_guide_use_case import EmergencyGuideUseCase
from safeteen.app.ports.output.emergency_guide_repository import EmergencyGuideRepository


class EmergencyGuideInteractor(EmergencyGuideUseCase):

    def __init__(self, repository: EmergencyGuideRepository) -> None:
        self._repository = repository

    def get_guide(self, command: EmergencyGuideCommand) -> EmergencyGuideResult:
        return self._repository.get_guide()
