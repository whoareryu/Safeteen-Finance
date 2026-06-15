from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.use_cases.passenger_jack_trainer_interactor import JackTrainerInteractor
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db
from titanic.adapter.outbound.pg.passenger_jack_trainer_pg_repository import JackTrainerPGRepository
from titanic.app.ports.output.passenger_jack_trainer_repository import JackTrainerRepository


"""
JackTrainer 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(JackTrainerPGRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(JackTrainerUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""


def get_jack_trainer_repository(
    db: AsyncSession = Depends(get_db)
) -> JackTrainerRepository:
    return JackTrainerPGRepository(session=db)


def get_jack_trainer_use_case(
    repository: JackTrainerRepository = Depends(get_jack_trainer_repository)
) -> JackTrainerUseCase:
    return JackTrainerInteractor(repository=repository)


