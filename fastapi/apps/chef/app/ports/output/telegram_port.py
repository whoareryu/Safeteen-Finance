from __future__ import annotations
from abc import ABC, abstractmethod

from chef.app.dtos.telegram_dto import TelegramQuery, TelegramResponse


class TelegramPort(ABC):

    @abstractmethod
    async def introduce_myself(self, query: TelegramQuery) -> TelegramResponse:
        pass
