from __future__ import annotations

import logging

from ....app.ports.output.crew_smith_captain_port import SmithCaptainPort
from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainResponse, SmithCaptainQuery, SmithChatCommand, SmithChatResponse
from sqlalchemy.ext.asyncio import AsyncSession
logger = logging.getLogger(__name__)


class SmithCaptainRepository(SmithCaptainPort):
    """SmithCaptainPortPort 구현."""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, schema: SmithCaptainQuery) -> SmithCaptainResponse:
        logger.info("[SmithCaptainRepository] introduce_myself 진입 | request_data={schema}")
        return SmithCaptainResponse(
            id=schema.id * 10000,
            name=schema.name + "가 레포지토리에 다녀옴"
        )

    async def chat(self, command: SmithChatCommand) -> SmithChatResponse:
        logger.info(f"[SmithCaptainRepository] chat 진입 | message={command.message}")
        return SmithChatResponse(reply=f"[Smith 선장]: '{command.message}' — 답변 준비 중입니다.")
