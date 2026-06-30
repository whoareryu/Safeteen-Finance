from __future__ import annotations

from chef.adapter.inbound.api.schemas.discord_schema import DiscordSchema
from chef.app.dtos.discord_dto import DiscordMessageCommand, DiscordMessageResult, DiscordQuery, DiscordResponse
from chef.app.ports.input.discord_use_case import DiscordUseCase
from chef.app.ports.output.discord_port import DiscordPort


class DiscordInteractor(DiscordUseCase):

    def __init__(self, repository: DiscordPort) -> None:
        self.repository = repository

    async def introduce_myself(self, query: DiscordQuery) -> DiscordResponse:
        schema = DiscordSchema(id=2, name="Chef Discord Bot")
        return DiscordResponse(id=schema.id, name=schema.name)

    async def receive_message(self, cmd: DiscordMessageCommand) -> DiscordMessageResult:
        return await self.repository.receive_message(cmd)
