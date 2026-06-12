from __future__ import annotations

import logging

from titanic.app.dtos.passenger_ruth_survivor_dto import RuthSurvivorResponse, RuthSurvivorQuery
from titanic.app.ports.output.passenger_ruth_survivor_repository import RuthSurvivorRepository
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class RuthSurvivorPGRepository(RuthSurvivorRepository):
    """RuthSurvivorRepository 구현."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def introduce_myself(self,query: RuthSurvivorQuery) -> RuthSurvivorResponse:
        logger.info("[RuthSurvivorPGRepository] introduce_myself called 진입 | request_data={query}")
        response: RuthSurvivorResponse = RuthSurvivorResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴"
        )
        return response
    