from __future__ import annotations

from chef.app.dtos.telegram_dto import TelegramQuery, TelegramResponse
from chef.app.ports.input.telegram_use_case import TelegramUseCase
from chef.app.ports.output.telegram_port import TelegramPort


class TelegramInteractor(TelegramUseCase):

    def __init__(self, repository: TelegramPort) -> None:
        self.repository = repository

    async def introduce_myself(self, query: TelegramQuery) -> TelegramResponse:
        return TelegramResponse(id=1, name="Chef Telegram Bot")
