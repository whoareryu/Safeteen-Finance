from titanic.app.ports.input.passenger_ruth_survivor_use_case import RuthSurvivorUseCase
from titanic.app.use_cases.passenger_ruth_survivor_interactor import RuthSurvivorInteractor
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db
from titanic.adapter.outbound.pg.passenger_ruth_survivor_pg_repository import RuthSurvivorPGRepository
from titanic.app.ports.output.passenger_ruth_survivor_repository import RuthSurvivorRepository


"""
RuthSurvivor 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(RuthSurvivorPGRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(RuthSurvivorUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""


def get_ruth_survivor_repository(
    db: AsyncSession = Depends(get_db)
) -> RuthSurvivorRepository:
    return RuthSurvivorPGRepository(session=db)


def get_ruth_survivor_use_case(
    repository: RuthSurvivorRepository = Depends(get_ruth_survivor_repository)
) -> RuthSurvivorUseCase:
    return RuthSurvivorInteractor(repository=repository)

