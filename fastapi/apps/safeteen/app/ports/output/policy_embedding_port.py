from __future__ import annotations

from abc import ABC, abstractmethod


class PolicyEmbeddingPort(ABC):
    """Outbound 출력 포트 — 정책 문서/조회어를 임베딩 벡터로 변환한다 (RAG 검색용)."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        pass
