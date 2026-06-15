from functools import lru_cache

from user.adapter.outbound.pg.meal_plan_pg_repository import MealPlanPgRepository
from user.app.ports.input.meal_plan_use_case import MealPlanUseCase
from user.app.ports.output.meal_plan_repository import IMealPlanRepository
from user.app.use_cases.meal_plan_interactor import MealPlanInteractor
from user.app.use_cases.strategies.recommendation_strategy import (
    BudgetBasedRecommendationStrategy,
)


@lru_cache
def get_meal_plan_use_case() -> MealPlanUseCase:
    repository: IMealPlanRepository = MealPlanPgRepository()
    return MealPlanInteractor(
        meal_plan_repo=repository,
        budget_strategy=BudgetBasedRecommendationStrategy(),
    )
