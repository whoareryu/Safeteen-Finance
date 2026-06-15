from functools import lru_cache

from restaurant.adapter.outbound.pg.today_picks_pg_repository import TodayPicksPgRepository
from restaurant.app.ports.input.today_picks_use_case import TodayPicksUseCase
from restaurant.app.ports.output.today_picks_repository import TodayPicksRepository
from restaurant.app.use_cases.today_picks_interactor import TodayPicksInteractor


@lru_cache
def get_today_picks_use_case() -> TodayPicksUseCase:
    repository: TodayPicksRepository = TodayPicksPgRepository()
    return TodayPicksInteractor(repository=repository)
