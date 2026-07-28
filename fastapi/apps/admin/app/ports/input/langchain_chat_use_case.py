from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.langchain_chat_dto import ChatCommand, ChatResult


class LangchainChatUseCase(ABC):
    """Inbound 입력 포트 — LangChain 어시스턴트와의 대화."""

    @abstractmethod
    async def chat(self, command: ChatCommand) -> ChatResult:
        pass
