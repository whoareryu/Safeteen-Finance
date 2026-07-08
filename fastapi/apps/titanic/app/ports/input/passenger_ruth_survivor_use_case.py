from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_ruth_survivor_dto import RuthSurvivorQuery, RuthSurvivorResponse


class RuthSurvivorUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/ruth_survivor_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: RuthSurvivorQuery) -> RuthSurvivorResponse:
        pass
