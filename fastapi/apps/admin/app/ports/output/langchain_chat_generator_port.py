from __future__ import annotations

from abc import ABC, abstractmethod


class LangchainChatGeneratorPort(ABC):
    """사용자 메시지에 대한 응답을 생성하는 outbound 포트.

    LangChain 등 구체 LLM 통합 클래스는 이 포트 뒤 adapter/outbound/client/에서만 참조한다.
    """

    @abstractmethod
    async def reply(self, message: str) -> str:
        pass
