from __future__ import annotations

from abc import ABC, abstractmethod

from safeteen.app.dtos.emergency_dto import EmergencyGuideCommand, EmergencyGuideResult


class EmergencyGuideUseCase(ABC):
    """Inbound 입력 포트 — 계좌 도용/사기 피해 발생 시 즉각 대응 가이드 조회."""

    @abstractmethod
    def get_guide(self, command: EmergencyGuideCommand) -> EmergencyGuideResult:
        pass
