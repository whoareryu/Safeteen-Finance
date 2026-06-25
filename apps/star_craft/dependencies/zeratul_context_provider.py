from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.matrix.gird_oracle_database_manager import get_db
from star_craft.adapter.outbound.repositories.zeratul_context_repository import ZeratulContextRepository
from star_craft.app.ports.input.zeratul_context_use_case import ZeratulContextUseCase
from star_craft.app.ports.output.zeratul_context_port import ZeratulContextPort
from star_craft.app.use_cases.zeratul_context_interactor import ZeratulContextInteractor

"""
ZeratulContext 의존성 조립소 (DIP 팩토리).
"""


def get_zeratul_context_repository(
    db: AsyncSession = Depends(get_db),
) -> ZeratulContextPort:
    return ZeratulContextRepository(session=db)


def get_zeratul_context_use_case(
    repository: ZeratulContextPort = Depends(get_zeratul_context_repository),
) -> ZeratulContextUseCase:
    return ZeratulContextInteractor(repository=repository)
