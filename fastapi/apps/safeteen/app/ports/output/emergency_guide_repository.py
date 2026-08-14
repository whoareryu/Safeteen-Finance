from __future__ import annotations

from abc import ABC, abstractmethod

from safeteen.app.dtos.emergency_dto import EmergencyGuideResult


class EmergencyGuideRepository(ABC):
    """Outbound 출력 포트 — 지급정지·경찰 신고 등 피해 대응 가이드 소스 (현재 Mock)."""

    @abstractmethod
    def get_guide(self) -> EmergencyGuideResult:
        pass
