from __future__ import annotations

from abc import ABC, abstractmethod

from safeteen.domain.value_objects.alternative_policy import AlternativePolicy


class PolicyUseCase(ABC):
    """Inbound 입력 포트 — 청년 대상 합법 금융 지원 정책 목록 조회."""

    @abstractmethod
    async def list_policies(self) -> list[AlternativePolicy]:
        pass
