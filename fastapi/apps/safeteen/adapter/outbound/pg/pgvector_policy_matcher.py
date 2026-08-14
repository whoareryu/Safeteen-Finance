from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from safeteen.adapter.outbound.mappers.policy_document_orm_mapper import to_entity
from safeteen.adapter.outbound.orm.policy_document_orm import PolicyDocumentORM
from safeteen.app.dtos.analysis_dto import RiskLevel
from safeteen.app.ports.output.policy_embedding_port import PolicyEmbeddingPort
from safeteen.app.ports.output.policy_matcher_port import PolicyMatcherPort
from safeteen.domain.value_objects.alternative_policy import AlternativePolicy


class PgVectorPolicyMatcher(PolicyMatcherPort):
    """Outbound 어댑터 — pgvector 코사인 유사도 검색으로 crime_type에 가장 가까운
    합법 대안 정책을 찾는다 (RAG)."""

    def __init__(self, session: AsyncSession, embedder: PolicyEmbeddingPort) -> None:
        self._session = session
        self._embedder = embedder

    async def match(self, crime_type: str, risk_level: RiskLevel) -> AlternativePolicy | None:
        if risk_level == "SAFE":
            return None

        query_embedding = await self._embedder.embed(crime_type)
        stmt = (
            select(PolicyDocumentORM)
            .order_by(PolicyDocumentORM.embedding.cosine_distance(query_embedding))
            .limit(1)
        )
        result = await self._session.execute(stmt)
        orm = result.scalars().first()
        return to_entity(orm) if orm is not None else None
