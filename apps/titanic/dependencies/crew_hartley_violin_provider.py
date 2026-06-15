from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.use_cases.crew_hartley_violin_interactor import HartleyViolinInteractor
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db
from titanic.adapter.outbound.pg.crew_hartley_violin_pg_repository import HartleyViolinPGRepository
from titanic.app.ports.output.crew_hartley_violin_repository import HartleyViolinRepository


"""
HartleyViolin 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(HartleyViolinPGRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(HartleyViolinUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""

def get_hartley_violin_repository(
    db: AsyncSession = Depends(get_db)
) -> HartleyViolinRepository:
    return HartleyViolinPGRepository(session=db)
  

def get_hartley_violin_use_case(
    repository: HartleyViolinRepository = Depends(get_hartley_violin_repository)
) -> HartleyViolinUseCase:
    return HartleyViolinInteractor(repository=repository)


