from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from safeteen.adapter.outbound.mappers.policy_document_orm_mapper import to_entity
from safeteen.adapter.outbound.orm.policy_document_orm import PolicyDocumentORM
from safeteen.app.ports.output.policy_repository import PolicyRepository
from safeteen.domain.value_objects.alternative_policy import AlternativePolicy


class PolicyPgRepository(PolicyRepository):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> list[AlternativePolicy]:
        result = await self._session.execute(select(PolicyDocumentORM).order_by(PolicyDocumentORM.id))
        return [to_entity(orm) for orm in result.scalars().all()]
