from silicon_valley.app.ports.input.piper_dinesh_dash_use_case import DineshDashUseCase
from silicon_valley.app.use_cases.piper_dinesh_dash_interactor import DineshDashInteractor
from silicon_valley.adapter.outbound.repositories.piper_dinesh_dash_repository import DineshDashRepository
from silicon_valley.app.ports.output.piper_dinesh_dash_port import DineshDashPort
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db

"""
DineshDash 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(DineshDashRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(DineshDashUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""


def get_dinesh_dash_repository(
    db: AsyncSession = Depends(get_db)
) -> DineshDashPort:
    return DineshDashRepository(session=db)


def get_dinesh_dash_use_case(
    repository: DineshDashPort = Depends(get_dinesh_dash_repository)
) -> DineshDashUseCase:
    return DineshDashInteractor(repository=repository)
