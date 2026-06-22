from silicon_valley.app.ports.input.piper_hendricks_ceo_use_case import HendricksCeoUseCase
from silicon_valley.app.use_cases.piper_hendricks_ceo_interactor import HendricksCeoInteractor
from silicon_valley.adapter.outbound.repositories.piper_hendricks_ceo_repository import HendricksCeoRepository
from silicon_valley.app.ports.output.piper_hendricks_ceo_port import HendricksCeoPort
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db

"""
HendricksCeo 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(HendricksCeoRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(HendricksCeoUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""


def get_hendricks_ceo_repository(
    db: AsyncSession = Depends(get_db)
) -> HendricksCeoPort:
    return HendricksCeoRepository(session=db)


def get_hendricks_ceo_use_case(
    repository: HendricksCeoPort = Depends(get_hendricks_ceo_repository)
) -> HendricksCeoUseCase:
    return HendricksCeoInteractor(repository=repository)
