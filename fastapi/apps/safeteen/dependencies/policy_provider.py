from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.database import get_db

from safeteen.adapter.outbound.pg.policy_pg_repository import PolicyPgRepository
from safeteen.app.ports.input.policy_use_case import PolicyUseCase
from safeteen.app.use_cases.policy_interactor import PolicyInteractor


def get_policy_use_case(db: AsyncSession = Depends(get_db)) -> PolicyUseCase:
    return PolicyInteractor(repository=PolicyPgRepository(session=db))
