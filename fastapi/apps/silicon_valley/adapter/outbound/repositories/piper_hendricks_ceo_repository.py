from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from silicon_valley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoQuery, HendricksCeoResponse
from silicon_valley.app.ports.output.piper_hendricks_ceo_port import HendricksCeoPort


class HendricksCeoRepository(HendricksCeoPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, schema: HendricksCeoQuery) -> HendricksCeoResponse:
        return HendricksCeoResponse(id=schema.id, name=schema.name)
