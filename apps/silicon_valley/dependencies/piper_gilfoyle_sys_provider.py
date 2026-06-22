from silicon_valley.app.ports.input.piper_gilfoyle_sys_use_case import GilfoyleSysUseCase
from silicon_valley.app.use_cases.piper_gilfoyle_sys_interactor import GilfoyleSysInteractor
from silicon_valley.adapter.outbound.repositories.piper_gilfoyle_sys_repository import GilfoyleSysRepository
from silicon_valley.app.ports.output.piper_gilfoyle_sys_port import GilfoyleSysPort
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from core.matrix.gird_oracle_database_manager import get_db

"""
GilfoyleSys 의존성 조립소 (DIP 팩토리).

DIP 원칙:
  - 라우터는 구현체(GilfoyleSysRepository)를 직접 알지 못한다.
  - 리턴 타입은 구현체가 아닌 포트(GilfoyleSysUseCase)로 선언한다.
  - 세션은 core 의 get_db 에서 주입받는다 (AsyncSession).
"""


def get_gilfoyle_sys_repository(
    db: AsyncSession = Depends(get_db)
) -> GilfoyleSysPort:
    return GilfoyleSysRepository(session=db)


def get_gilfoyle_sys_use_case(
    repository: GilfoyleSysPort = Depends(get_gilfoyle_sys_repository)
) -> GilfoyleSysUseCase:
    return GilfoyleSysInteractor(repository=repository)
