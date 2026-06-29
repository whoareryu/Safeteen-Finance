from functools import lru_cache

from restaurant.adapter.outbound.pg.course_recommendation_pg_repository import (
    CourseRecommendationPgRepository,
)
from restaurant.app.ports.input.course_recommendation_use_case import (
    CourseRecommendationUseCase,
)
from restaurant.app.use_cases.course_recommendation_interactor import (
    CourseRecommendationInteractor,
)


@lru_cache
def get_course_recommendation_use_case() -> CourseRecommendationUseCase:
    return CourseRecommendationInteractor(
        repository=CourseRecommendationPgRepository()
    )
