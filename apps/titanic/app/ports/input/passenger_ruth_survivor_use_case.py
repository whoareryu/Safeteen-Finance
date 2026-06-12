from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from titanic.adapter.inbound.api.schemas.passenger_ruth_survivor_schema import RuthSurvivorSchema
from titanic.app.dtos.passenger_ruth_survivor_dto import RuthSurvivorResponse


class RuthSurvivorUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/ruth_survivor_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self,schema: list[RuthSurvivorSchema]) -> RuthSurvivorResponse:
        pass
