from __future__ import annotations

import logging

from titanic.app.dtos.passenger_ruth_survivor_dto import RuthSurvivorResponse, RuthSurvivorQuery
from titanic.app.ports.output.passenger_ruth_survivor_port import RuthSurvivorPort
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class RuthSurvivorRepository(RuthSurvivorPort):
    """RuthSurvivorPort 구현."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    
    async def introduce_myself(self, schema: RuthSurvivorQuery) -> RuthSurvivorResponse:
        logger.info("[RuthSurvivorRepository] introduce_myself called 진입 | request_data={schema}")
        response: RuthSurvivorResponse = RuthSurvivorResponse(
            id=schema.id * 10000,
            name=schema.name + "가 레포지토리에 다녀옴"
        )
        return response
    