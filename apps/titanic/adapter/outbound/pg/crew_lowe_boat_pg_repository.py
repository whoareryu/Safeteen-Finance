from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse
from titanic.app.ports.output.crew_lowe_boat_repository import LoweBoatRepository

logger = logging.getLogger(__name__)


class LoweBoatPGRepository(LoweBoatRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: LoweBoatQuery) -> LoweBoatResponse:
        return LoweBoatResponse(id=query.id * 10000, name=query.name)
