from silicon_valley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from silicon_valley.app.use_cases.piper_bighetti_hr_interactor import BighettiHrInteractor
from silicon_valley.adapter.outbound.repositories.piper_bighetti_hr_repository import BighettiHrRepository
from silicon_valley.app.ports.output.piper_bighetti_hr_port import BighettiHrPort
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db

"""
BighettiHr 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(BighettiHrRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(BighettiHrUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""


def get_bighetti_hr_repository(
    db: AsyncSession = Depends(get_db)
) -> BighettiHrPort:
    return BighettiHrRepository(session=db)


def get_bighetti_hr_use_case(
    repository: BighettiHrPort = Depends(get_bighetti_hr_repository)
) -> BighettiHrUseCase:
    return BighettiHrInteractor(repository=repository)
