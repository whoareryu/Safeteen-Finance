from titanic.app.ports.input.passenger_molly_scaler_use_case import MollyScalerUseCase
from titanic.app.use_cases.passenger_molly_scaler_interactor import MollyScalerInteractor
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db
from titanic.adapter.outbound.pg.passenger_molly_scaler_pg_repository import MollyScalerPGRepository
from titanic.app.ports.output.passenger_molly_scaler_repository import MollyScalerRepository


"""
MollyScaler 의존성 조립소 (DIP 팩토리).

DIP 원칙:
- 라우터는 구현체(MollyScalerPGRepository)를 직접 알지 못한다.
- 리턴 타입은 구현체가 아닌 포트(MollyScalerUseCase)로 선언한다.
- 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""


def get_molly_scaler_repository(
    db: AsyncSession = Depends(get_db)
) -> MollyScalerRepository:
    return MollyScalerPGRepository(session=db)


def get_passenger_molly_scaler_use_case(
    repository: MollyScalerRepository = Depends(get_molly_scaler_repository)
) -> MollyScalerUseCase:
    return MollyScalerInteractor(repository=repository)

