from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse, SmithChatCommand, SmithChatResponse


class SmithCaptainRepository(ABC):

    @abstractmethod
    async def introduce_myself(self, query: SmithCaptainQuery) -> SmithCaptainResponse:
        pass

    @abstractmethod
    async def chat(self, command: SmithChatCommand) -> SmithChatResponse:
        pass
