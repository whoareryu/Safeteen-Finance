from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.checkin_dto import CheckinCommand, CheckinResult


class CheckinUseCase(ABC):
    """Inbound 입력 포트 — 일일 출석체크(사진 진단 → 건강점수·포인트·스트릭·뱃지)."""

    @abstractmethod
    async def checkin(self, command: CheckinCommand) -> CheckinResult:
        pass
