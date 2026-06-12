from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schema import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinResponse

class HartleyViolinUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/hartley_violin_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self,schema: list[HartleyViolinSchema]) -> HartleyViolinResponse:
        """Hartley 바이올린을 조회한다."""
        pass
