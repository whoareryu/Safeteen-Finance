from functools import lru_cache

from gourmet.adapter.outbound.pg.daily_pick_pg_repository import DailyPickPgRepository
from gourmet.app.ports.input.daily_pick_use_case import DailyPickUseCase
from gourmet.app.ports.output.daily_pick_repository import DailyPickRepository
from gourmet.app.use_cases.daily_pick_interactor import DailyPickInteractor


@lru_cache
def get_daily_pick_use_case() -> DailyPickUseCase:
    repository: DailyPickRepository = DailyPickPgRepository()
    return DailyPickInteractor(repository=repository)
