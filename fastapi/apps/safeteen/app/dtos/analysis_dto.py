from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from safeteen.domain.value_objects.alternative_policy import AlternativePolicy

RiskLevel = Literal["SAFE", "WARNING", "DANGER"]


@dataclass(frozen=True)
class AnalyzeCommand:
    text: str | None
    image_bytes: bytes | None
    image_content_type: str | None


@dataclass(frozen=True)
class AnalysisResult:
    risk_level: RiskLevel
    risk_score: int
    detected_terms: list[str]
    crime_type: str
    legal_warning: str
    fact_check_summary: str
    alternative_policy: AlternativePolicy | None
