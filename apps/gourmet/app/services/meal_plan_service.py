"""식비 플랜 — Strategy 기반 추천."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from apps.gourmet.app.models.meal_plan import MealPlan
from apps.gourmet.app.models.restaurant import Restaurant
from apps.gourmet.app.repositories.interfaces import IMealPlanRepository
from apps.gourmet.app.repositories.meal_plan_repository import MealPlanRepository
from apps.gourmet.app.services.strategies.recommendation_strategy import (
    BudgetBasedRecommendationStrategy,
    RecommendationContext,
    RecommendationStrategy,
)


class MealPlanService:
    """플랜 조회·저장 및 예산 내 맛집 추천 (Strategy 주입)."""

    def __init__(
        self,
        meal_plan_repo: IMealPlanRepository | None = None,
        budget_strategy: RecommendationStrategy | None = None,
    ) -> None:
        self._meal_plans = meal_plan_repo or MealPlanRepository()
        self._budget_strategy = budget_strategy or BudgetBasedRecommendationStrategy()

    def get_current_plan(
        self, db: Session, user_id: int, on_date: date | None = None
    ) -> MealPlan | None:
        plan = self._meal_plans.get_active_for_user(
            db, user_id, on_date or date.today()
        )
        if plan is not None and not plan.belongs_to_user(user_id):
            return None
        return plan

    def upsert_plan(
        self,
        db: Session,
        *,
        user_id: int,
        monthly_budget: int,
        spent_amount: int,
        period_start: date,
        period_end: date,
    ) -> MealPlan:
        plan = MealPlan(
            user_id=user_id,
            monthly_budget=monthly_budget,
            spent_amount=spent_amount,
            period_start=period_start,
            period_end=period_end,
        )
        return self._meal_plans.save(db, plan)

    def remaining_budget(self, plan: MealPlan) -> int:
        return max(0, plan.monthly_budget - plan.spent_amount)

    def restaurants_within_plan(
        self,
        db: Session,
        user_id: int,
        *,
        category_slug: str | None = None,
        offset: int = 0,
        limit: int = 20,
        on_date: date | None = None,
    ) -> tuple[list[Restaurant], int, MealPlan | None]:
        plan = self.get_current_plan(db, user_id, on_date)
        if plan is None:
            return [], 0, None

        ctx = RecommendationContext(
            offset=offset,
            limit=limit,
            category_slug=category_slug,
            meal_plan=plan,
            on_date=on_date or date.today(),
        )
        result = self._budget_strategy.recommend(db, ctx)
        return result.restaurants, result.meta_cap, plan
