from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.care_guide_dto import CareGuideCommand, CareGuideResult


class CareGuideUseCase(ABC):
    """Inbound 입력 포트 — 진단 결과를 한국어 케어 처방 문구로 변환."""

    @abstractmethod
    async def generate(self, command: CareGuideCommand) -> CareGuideResult:
        pass
