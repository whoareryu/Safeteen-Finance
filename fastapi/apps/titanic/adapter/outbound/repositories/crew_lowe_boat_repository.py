from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse
from titanic.app.ports.output.crew_lowe_boat_port import LoweBoatPort

logger = logging.getLogger(__name__)


class LoweBoatRepository(LoweBoatPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: LoweBoatQuery) -> LoweBoatResponse:
        return LoweBoatResponse(id=schema.id * 10000, name=schema.name)
