from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.tutorial_dto import (
    TutorialCreateCommand,
    TutorialMoveLightCommand,
    TutorialStateResult,
)


class TutorialUseCase(ABC):
    """Inbound 입력 포트 — 식집사 튜토리얼(가상 식물 연습) 상태 관리."""

    @abstractmethod
    async def create(self, command: TutorialCreateCommand) -> TutorialStateResult:
        pass

    @abstractmethod
    async def get(self, tutorial_plant_id: int) -> TutorialStateResult:
        pass

    @abstractmethod
    async def get_active_for_owner(self, owner_user_id: int) -> TutorialStateResult | None:
        pass

    @abstractmethod
    async def water(self, tutorial_plant_id: int) -> TutorialStateResult:
        pass

    @abstractmethod
    async def add_nutrient(self, tutorial_plant_id: int) -> TutorialStateResult:
        pass

    @abstractmethod
    async def move_light(self, command: TutorialMoveLightCommand) -> TutorialStateResult:
        pass

    @abstractmethod
    async def check_leaves(self, tutorial_plant_id: int) -> TutorialStateResult:
        pass
