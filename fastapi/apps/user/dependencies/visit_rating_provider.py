from functools import lru_cache

from user.adapter.outbound.pg.visit_rating_pg_repository import (
    VisitRatingPgRepository,
)
from user.app.ports.input.visit_rating_use_case import VisitRatingUseCase
from user.app.use_cases.visit_rating_interactor import VisitRatingInteractor


@lru_cache
def get_visit_rating_use_case() -> VisitRatingUseCase:
    return VisitRatingInteractor(repository=VisitRatingPgRepository())
