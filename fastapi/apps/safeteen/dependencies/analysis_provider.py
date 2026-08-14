from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db

from safeteen.adapter.outbound.llm.gemini_analysis_adapter import GeminiAnalysisAdapter
from safeteen.adapter.outbound.llm.gemini_policy_embedding_adapter import GeminiPolicyEmbeddingAdapter
from safeteen.adapter.outbound.pg.pgvector_policy_matcher import PgVectorPolicyMatcher
from safeteen.app.ports.input.analysis_use_case import AnalysisUseCase
from safeteen.app.use_cases.analysis_interactor import AnalysisInteractor


def get_analysis_use_case(db: AsyncSession = Depends(get_db)) -> AnalysisUseCase:
    return AnalysisInteractor(
        model=GeminiAnalysisAdapter(),
        policy_matcher=PgVectorPolicyMatcher(session=db, embedder=GeminiPolicyEmbeddingAdapter()),
    )
