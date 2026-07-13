from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from admin.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse
from admin.app.ports.output.piper_dinesh_dash_port import DineshDashPort


class DineshDashRepository(DineshDashPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, schema: DineshDashQuery) -> DineshDashResponse:
        return DineshDashResponse(id=schema.id, name=schema.name)
