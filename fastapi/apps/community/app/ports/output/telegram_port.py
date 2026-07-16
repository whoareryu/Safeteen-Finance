from __future__ import annotations
from abc import ABC, abstractmethod

from community.app.dtos.telegram_dto import TelegramQuery, TelegramResponse
from community.domain.entities.telegram_message_entity import TelegramMessageEntity


class TelegramPort(ABC):

    @abstractmethod
    async def introduce_myself(self, query: TelegramQuery) -> TelegramResponse:
        pass

    @abstractmethod
    async def save_message(self, entity: TelegramMessageEntity) -> TelegramMessageEntity:
        pass

    @abstractmethod
    async def list_messages(self, limit: int) -> list[TelegramMessageEntity]:
        pass
