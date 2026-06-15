from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.use_cases.crew_andrews_architect_interactor import AndrewsArchitectInteractor
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db
from titanic.adapter.outbound.pg.crew_andrews_architect_pg_repository import AndrewsArchitectPGRepository
from titanic.app.ports.output.crew_andrews_architect_repository import AndrewsArchitectRepository


"""
AndrewsArchitect 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(AndrewsArchitectPGRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(AndrewsArchitectUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""

def get_andrews_architect_repository(
    db: AsyncSession = Depends(get_db)
) -> AndrewsArchitectRepository:
        return AndrewsArchitectPGRepository(session=db)
  
  
def get_andrews_architect_use_case(
    repository : AndrewsArchitectRepository = Depends(get_andrews_architect_repository)
) -> AndrewsArchitectUseCase:
    return AndrewsArchitectInteractor(repository=repository)


