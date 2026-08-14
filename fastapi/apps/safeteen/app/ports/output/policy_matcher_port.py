from __future__ import annotations

from abc import ABC, abstractmethod

from safeteen.app.dtos.analysis_dto import RiskLevel
from safeteen.domain.value_objects.alternative_policy import AlternativePolicy


class PolicyMatcherPort(ABC):
    """Outbound 출력 포트 — 분석된 범죄 유형/위험도에 맞는 합법 대안 정책을 매칭한다."""

    @abstractmethod
    async def match(self, crime_type: str, risk_level: RiskLevel) -> AlternativePolicy | None:
        pass
