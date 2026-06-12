from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from titanic.adapter.inbound.api.schemas.passenger_rose_model_schema import RoseModelSchema
from titanic.app.dtos.passenger_rose_model_dto import RoseModelResponse


class RoseModelUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/rose_model_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self,schema: list[RoseModelSchema]) -> RoseModelResponse:
        pass
