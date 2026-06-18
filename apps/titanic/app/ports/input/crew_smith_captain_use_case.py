from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_smith_captain_dto import (
    SmithCaptainQuery,
    SmithCaptainResponse,
    SmithChatCommand,
    SmithChatResponse,
)


class SmithCaptainUseCase(ABC):
    """Inbound 입력 포트 — adapter/inbound/api/v1/smith_captain_router.py 와 대응."""

    @abstractmethod
    async def introduce_myself(self, schema: SmithCaptainQuery) -> SmithCaptainResponse:
        """Smith 선장 정보를 조회한다."""
        pass

    @abstractmethod
    async def chat(self, command: SmithChatCommand) -> SmithChatResponse:
        """사용자의 자연어 입력을 받아 응답한다."""
        pass
