from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.matrix.gird_oracle_database_manager import get_db
from titanic.adapter.outbound.pg.james_director_pg_repository import JamesDirectorPgRepository
from titanic.app.ports.input.james_director_use_case import JamesDirectorUseCase
from titanic.app.ports.output.james_director_repository import JamesDirectorRepository
from titanic.app.use_cases.james_direcrtor_interactor import JamesDirectorInteractor

"""
JamesDirector 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(JamesDirectorPgRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(JamesDirectorUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""


def get_james_director_use_case(
    db: AsyncSession = Depends(get_db),
) -> JamesDirectorUseCase:
    repository: JamesDirectorRepository = JamesDirectorPgRepository(session=db)
    return JamesDirectorInteractor(repository=repository)


