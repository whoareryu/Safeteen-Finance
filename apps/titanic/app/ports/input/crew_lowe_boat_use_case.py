from __future__ import annotations
from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema
from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatResponse
from typing import Any


class LoweBoatUseCase(ABC):
    """Inbound input port."""
    @abstractmethod
    async def introduce_myself(self,schema: list[LoweBoatSchema]) -> LoweBoatResponse:
        pass
