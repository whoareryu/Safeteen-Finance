from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse


class DineshDashPort(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: DineshDashQuery) -> DineshDashResponse:
        pass
