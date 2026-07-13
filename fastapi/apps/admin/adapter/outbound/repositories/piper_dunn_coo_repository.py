from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from admin.app.dtos.piper_dunn_coo_dto import DunnCooQuery, DunnCooResponse
from admin.app.ports.output.piper_dunn_coo_port import DunnCooPort


class DunnCooRepository(DunnCooPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, schema: DunnCooQuery) -> DunnCooResponse:
        return DunnCooResponse(id=schema.id, name=schema.name)
