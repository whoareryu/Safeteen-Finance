from __future__ import annotations

from abc import ABC, abstractmethod

from plant.app.dtos.chat_dto import ChatCommand, ChatResult


class ChatUseCase(ABC):
    """Inbound 입력 포트 — RAG 기반 식물 채팅."""

    @abstractmethod
    async def chat(self, command: ChatCommand) -> ChatResult:
        pass
