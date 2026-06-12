from __future__ import annotations

import logging

from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinResponse, HartleyViolinQuery
from titanic.app.ports.output.crew_hartley_violin_repository import HartleyViolinRepository
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class HartleyViolinPGRepository(HartleyViolinRepository):
    """HartleyViolinRepositoryPort 구현."""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        
    async def introduce_myself(self, query: HartleyViolinQuery) -> HartleyViolinResponse:
        logger.info(f"[HartleyViolinPGRepository] introduce_myself 진입 | request_data={query}")
        reponse: HartleyViolinResponse = HartleyViolinResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴"
        )
        return reponse
