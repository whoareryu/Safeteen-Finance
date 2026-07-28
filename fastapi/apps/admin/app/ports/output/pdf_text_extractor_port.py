from __future__ import annotations

from abc import ABC, abstractmethod


class PdfTextExtractorPort(ABC):
    """PDF 바이너리에서 텍스트를 추출하는 outbound 포트.

    구체 추출 라이브러리(neo4j_graphrag 등)는 이 포트 뒤 adapter/outbound/client/에서만 참조한다.
    """

    @abstractmethod
    async def extract(self, filename: str, data: bytes) -> str:
        pass
