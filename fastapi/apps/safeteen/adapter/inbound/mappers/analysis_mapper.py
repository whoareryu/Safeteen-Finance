from __future__ import annotations

from safeteen.adapter.inbound.api.schemas.analysis_schema import (
    AlternativePolicyResponse,
    AnalysisResultResponse,
)
from safeteen.app.dtos.analysis_dto import AnalysisResult


def to_response(result: AnalysisResult) -> AnalysisResultResponse:
    return AnalysisResultResponse(
        risk_level=result.risk_level,
        risk_score=result.risk_score,
        detected_terms=result.detected_terms,
        crime_type=result.crime_type,
        legal_warning=result.legal_warning,
        fact_check_summary=result.fact_check_summary,
        alternative_policy=(
            AlternativePolicyResponse(
                title=result.alternative_policy.title,
                description=result.alternative_policy.description,
                official_link=result.alternative_policy.official_link,
            )
            if result.alternative_policy
            else None
        ),
    )
