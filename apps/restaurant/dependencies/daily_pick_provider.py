from functools import lru_cache

from restaurant.adapter.outbound.pg.daily_pick_pg_repository import DailyPickPgRepository
from restaurant.app.ports.input.daily_pick_use_case import DailyPickUseCase
from restaurant.app.ports.output.daily_pick_repository import DailyPickRepository
from restaurant.app.use_cases.daily_pick_interactor import DailyPickInteractor


@lru_cache
def get_daily_pick_use_case() -> DailyPickUseCase:
    repository: DailyPickRepository = DailyPickPgRepository()
    return DailyPickInteractor(repository=repository)
