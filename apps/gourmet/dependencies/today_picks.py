from functools import lru_cache

from gourmet.adapter.outbound.pg.today_picks_pg_repository import TodayPicksPgRepository
from gourmet.app.ports.input.today_picks_use_case import TodayPicksUseCase
from gourmet.app.ports.output.today_picks_repository import TodayPicksRepository
from gourmet.app.use_cases.today_picks_interactor import TodayPicksInteractor


@lru_cache
def get_today_picks_use_case() -> TodayPicksUseCase:
    repository: TodayPicksRepository = TodayPicksPgRepository()
    return TodayPicksInteractor(repository=repository)
