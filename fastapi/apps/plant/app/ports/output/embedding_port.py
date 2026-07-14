from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """텍스트 → 벡터 임베딩 출력 포트."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        pass
