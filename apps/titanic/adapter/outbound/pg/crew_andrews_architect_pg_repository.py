from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectQuery, AndrewsArchitectResponse
from titanic.app.ports.output.crew_andrews_architect_repository import AndrewsArchitectRepository

logger = logging.getLogger(__name__)


class AndrewsArchitectPGRepository(AndrewsArchitectRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: AndrewsArchitectQuery) -> AndrewsArchitectResponse:
        return AndrewsArchitectResponse(id=query.id * 10000, name=query.name)
