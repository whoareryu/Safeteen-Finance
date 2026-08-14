from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class AlternativePolicyResponse(BaseModel):
    title: str
    description: str
    official_link: str


class AnalysisResultResponse(BaseModel):
    risk_level: Literal["SAFE", "WARNING", "DANGER"]
    risk_score: int
    detected_terms: list[str]
    crime_type: str
    legal_warning: str
    fact_check_summary: str
    alternative_policy: AlternativePolicyResponse | None = None
