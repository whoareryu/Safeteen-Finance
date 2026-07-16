from __future__ import annotations

from datetime import datetime, timezone

from community.app.dtos.telegram_dto import TelegramQuery, TelegramResponse
from community.app.ports.input.telegram_use_case import TelegramUseCase
from community.app.ports.output.telegram_gateway import TelegramGateway
from community.app.ports.output.telegram_port import TelegramPort
from community.domain.entities.telegram_message_entity import TelegramMessageEntity


class TelegramInteractor(TelegramUseCase):

    def __init__(self, repository: TelegramPort, gateway: TelegramGateway) -> None:
        self.repository = repository
        self.gateway = gateway

    async def introduce_myself(self, query: TelegramQuery) -> TelegramResponse:
        return TelegramResponse(id=1, name="Chef Telegram Bot")

    async def send(self, text: str) -> TelegramMessageEntity:
        await self.gateway.send(text)
        return await self.repository.save_message(
            TelegramMessageEntity(id=None, text=text, sent_at=datetime.now(timezone.utc))
        )

    async def list_history(self, limit: int) -> list[TelegramMessageEntity]:
        return await self.repository.list_messages(limit)
