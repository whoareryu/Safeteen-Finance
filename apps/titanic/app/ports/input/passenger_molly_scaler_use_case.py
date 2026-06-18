from __future__ import annotations
from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerQuery, MollyScalerResponse


class MollyScalerUseCase(ABC):
    """Inbound input port."""
    @abstractmethod
    async def introduce_myself(self, schema: MollyScalerQuery) -> MollyScalerResponse:
        pass
