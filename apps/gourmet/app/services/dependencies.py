"""FastAPI Depends — Service·Strategy 조립 (싱글톤 모듈 변수 대신)."""

from __future__ import annotations

from functools import lru_cache

from apps.gourmet.app.services.meal_plan_service import MealPlanService
from apps.gourmet.app.services.restaurant_detail_service import RestaurantDetailService
from apps.gourmet.app.services.restaurant_domain_service import RestaurantDomainService
from apps.gourmet.app.services.strategies.recommendation_strategy import (
    BudgetBasedRecommendationStrategy,
    CategoryBrowseRecommendationStrategy,
)


@lru_cache
def get_restaurant_detail_service() -> RestaurantDetailService:
    return RestaurantDetailService()


@lru_cache
def get_restaurant_domain_service() -> RestaurantDomainService:
    return RestaurantDomainService()


@lru_cache
def get_meal_plan_service() -> MealPlanService:
    return MealPlanService(
        budget_strategy=BudgetBasedRecommendationStrategy(),
    )


@lru_cache
def get_category_browse_strategy() -> CategoryBrowseRecommendationStrategy:
    return CategoryBrowseRecommendationStrategy()
