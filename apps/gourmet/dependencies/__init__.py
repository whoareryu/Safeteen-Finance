"""FastAPI Depends — Service·Strategy 조립 (싱글톤 모듈 변수 대신)."""

from __future__ import annotations

from functools import lru_cache

from gourmet.app.ports.input.meal_plan_use_case import MealPlanUseCase
from gourmet.dependencies.meal_plan import get_meal_plan_use_case
from gourmet.app.use_cases.restaurant_detail_interactor import RestaurantDetailInteractor
from gourmet.app.ports.input.restaurant_use_case import RestaurantUseCase
from gourmet.dependencies.restaurant import get_restaurant_use_case
from gourmet.app.use_cases.strategies.recommendation_strategy import (
    BudgetBasedRecommendationStrategy,
    CategoryBrowseRecommendationStrategy,
)


@lru_cache
def get_restaurant_detail_service() -> RestaurantDetailInteractor:
    return RestaurantDetailInteractor()


@lru_cache
def get_restaurant_domain_service() -> RestaurantUseCase:
    return get_restaurant_use_case()


@lru_cache
def get_meal_plan_service() -> MealPlanUseCase:
    return get_meal_plan_use_case()


@lru_cache
def get_category_browse_strategy() -> CategoryBrowseRecommendationStrategy:
    return CategoryBrowseRecommendationStrategy()
