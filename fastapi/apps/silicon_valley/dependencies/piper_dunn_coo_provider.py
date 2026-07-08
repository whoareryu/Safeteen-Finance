from silicon_valley.app.ports.input.piper_dunn_coo_use_case import DunnCooUseCase
from silicon_valley.app.use_cases.piper_dunn_coo_interactor import DunnCooInteractor
from silicon_valley.adapter.outbound.repositories.piper_dunn_coo_repository import DunnCooRepository
from silicon_valley.app.ports.output.piper_dunn_coo_port import DunnCooPort
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db

"""
DunnCoo 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(DunnCooRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(DunnCooUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""


def get_dunn_coo_repository(
    db: AsyncSession = Depends(get_db)
) -> DunnCooPort:
    return DunnCooRepository(session=db)


def get_dunn_coo_use_case(
    repository: DunnCooPort = Depends(get_dunn_coo_repository)
) -> DunnCooUseCase:
    return DunnCooInteractor(repository=repository)
