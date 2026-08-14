from __future__ import annotations

from abc import ABC, abstractmethod

from safeteen.domain.value_objects.alternative_policy import AlternativePolicy


class PolicyRepository(ABC):
    """Outbound 출력 포트 — 청년 금융 지원 정책 소스 (현재 Mock, 추후 RAG/DB로 교체 가능)."""

    @abstractmethod
    async def list_all(self) -> list[AlternativePolicy]:
        pass
