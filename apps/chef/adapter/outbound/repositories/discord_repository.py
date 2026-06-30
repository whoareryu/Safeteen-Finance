from __future__ import annotations
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from chef.app.dtos.discord_dto import DiscordMessageCommand, DiscordMessageResult, DiscordQuery, DiscordResponse
from chef.app.ports.output.discord_port import DiscordPort

logger = logging.getLogger(__name__)


class DiscordRepository(DiscordPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: DiscordQuery) -> DiscordResponse:
        return DiscordResponse(id=query.id, name=query.name)

    async def receive_message(self, cmd: DiscordMessageCommand) -> DiscordMessageResult:
        return DiscordMessageResult(channel_id=cmd.channel_id, bot_reply=f"[echo] {cmd.content}")
