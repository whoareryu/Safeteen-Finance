from functools import lru_cache

from gourmet.adapter.outbound.pg.meal_plan_pg_repository import MealPlanPgRepository
from gourmet.app.ports.input.meal_plan_use_case import MealPlanUseCase
from gourmet.app.ports.output.meal_plan_repository import IMealPlanRepository
from gourmet.app.use_cases.meal_plan_interactor import MealPlanInteractor
from gourmet.app.use_cases.strategies.recommendation_strategy import (
    BudgetBasedRecommendationStrategy,
)


@lru_cache
def get_meal_plan_use_case() -> MealPlanUseCase:
    repository: IMealPlanRepository = MealPlanPgRepository()
    return MealPlanInteractor(
        meal_plan_repo=repository,
        budget_strategy=BudgetBasedRecommendationStrategy(),
    )
