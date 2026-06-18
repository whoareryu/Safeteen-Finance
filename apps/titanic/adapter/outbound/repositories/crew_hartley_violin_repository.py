from __future__ import annotations

import logging

from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinResponse, HartleyViolinQuery
from titanic.app.ports.output.crew_hartley_violin_port import HartleyViolinPort
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class HartleyViolinRepository(HartleyViolinPort):
    """HartleyViolinPortPort 구현."""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def introduce_myself(self, schema: HartleyViolinQuery) -> HartleyViolinResponse:
        logger.info(f"[HartleyViolinRepository] introduce_myself 진입 | request_data={schema}")
        reponse: HartleyViolinResponse = HartleyViolinResponse(
            id=schema.id * 10000,
            name=schema.name + "가 레포지토리에 다녀옴"
        )
        return reponse
