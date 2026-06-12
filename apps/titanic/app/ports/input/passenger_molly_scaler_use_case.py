from __future__ import annotations
from abc import ABC, abstractmethod
from titanic.adapter.inbound.api.schemas.passenger_molly_scaler_schema import MollyScalerSchema
from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerResponse
from typing import Any


class MollyScalerUseCase(ABC):
    """Inbound input port."""
    @abstractmethod
    async def introduce_myself(self,schema: list[MollyScalerSchema]) -> MollyScalerResponse:
        pass
