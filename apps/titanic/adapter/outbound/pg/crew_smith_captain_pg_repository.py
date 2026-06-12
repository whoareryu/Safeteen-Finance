from __future__ import annotations

import logging

from ....app.ports.output.crew_smith_captain_repository import SmithCaptainRepository
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainResponse, SmithCaptainQuery, SmithChatCommand, SmithChatResponse
from sqlalchemy.ext.asyncio import AsyncSession
logger = logging.getLogger(__name__)


class SmithCaptainPGRepository(SmithCaptainRepository):
    """SmithCaptainRepositoryPort 구현."""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: SmithCaptainQuery) -> SmithCaptainResponse:
        logger.info("[SmithCaptainPGRepository] introduce_myself 진입 | request_data={query}")
        return SmithCaptainResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴"
        )

    async def chat(self, command: SmithChatCommand) -> SmithChatResponse:
        logger.info(f"[SmithCaptainPGRepository] chat 진입 | message={command.message}")
        return SmithChatResponse(reply=f"[Smith 선장]: '{command.message}' — 답변 준비 중입니다.")
