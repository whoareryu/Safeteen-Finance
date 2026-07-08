from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_smith_captain_dto import SmithCaptainQuery, SmithCaptainResponse, SmithChatCommand, SmithChatResponse


class SmithCaptainPort(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: SmithCaptainQuery) -> SmithCaptainResponse:
        pass

    @abstractmethod
    async def chat(self, command: SmithChatCommand) -> SmithChatResponse:
        pass
