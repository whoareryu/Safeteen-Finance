from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from chef.app.dtos.telegram_dto import TelegramQuery, TelegramResponse
from chef.app.ports.output.telegram_port import TelegramPort


class TelegramRepository(TelegramPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: TelegramQuery) -> TelegramResponse:
        return TelegramResponse(id=query.id, name=query.name)
