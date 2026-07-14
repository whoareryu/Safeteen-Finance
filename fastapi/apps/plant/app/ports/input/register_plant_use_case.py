from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.register_plant_dto import RegisterPlantCommand, RegisterPlantResult


class RegisterPlantUseCase(ABC):
    """Inbound 입력 포트 — 마이플랜트 등록(수기 입력 또는 사진 자동 종 인식)."""

    @abstractmethod
    async def register(self, command: RegisterPlantCommand) -> RegisterPlantResult:
        pass
