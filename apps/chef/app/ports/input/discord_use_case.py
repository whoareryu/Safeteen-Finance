from __future__ import annotations
from abc import ABC, abstractmethod

from chef.app.dtos.discord_dto import DiscordMessageCommand, DiscordMessageResult, DiscordQuery, DiscordResponse


class DiscordUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, query: DiscordQuery) -> DiscordResponse:
        pass

    @abstractmethod
    async def receive_message(self, cmd: DiscordMessageCommand) -> DiscordMessageResult:
        pass
