from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysQuery, GilfoyleSysResponse
from silicon_valley.app.ports.output.piper_gilfoyle_sys_port import GilfoyleSysPort


class GilfoyleSysRepository(GilfoyleSysPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, schema: GilfoyleSysQuery) -> GilfoyleSysResponse:
        return GilfoyleSysResponse(id=schema.id, name=schema.name)
