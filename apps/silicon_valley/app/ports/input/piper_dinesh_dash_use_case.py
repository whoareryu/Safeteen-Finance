from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse


class DineshDashUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/piper_dinesh_dash_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: DineshDashQuery) -> DineshDashResponse:
        pass
