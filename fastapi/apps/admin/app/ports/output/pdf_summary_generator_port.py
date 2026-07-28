from __future__ import annotations

from abc import ABC, abstractmethod


class PdfSummaryGeneratorPort(ABC):
    """추출된 텍스트를 요약하는 outbound 포트.

    LangChain 등 구체 LLM 통합 클래스는 이 포트 뒤 adapter/outbound/client/에서만 참조한다.
    """

    @abstractmethod
    async def summarize(self, text: str) -> str:
        pass
