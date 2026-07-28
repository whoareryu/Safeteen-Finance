from __future__ import annotations

from admin.app.dtos.langchain_chat_dto import ChatCommand, ChatResult
from admin.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from admin.app.ports.output.langchain_chat_generator_port import LangchainChatGeneratorPort


class LangchainChatInteractor(LangchainChatUseCase):

    def __init__(self, generator: LangchainChatGeneratorPort) -> None:
        self._generator = generator

    async def chat(self, command: ChatCommand) -> ChatResult:
        reply = await self._generator.reply(command.message)
        return ChatResult(reply=reply)
