"""식비 플랜 — Strategy 기반 추천."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from user.adapter.outbound.orm.meal_plan_orm import MealPlan
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from user.app.dtos.meal_plan_dto import MealPlanIntroResponse
from user.app.ports.input.meal_plan_use_case import MealPlanUseCase
from user.app.ports.output.meal_plan_repository import IMealPlanRepository
from user.adapter.outbound.pg.meal_plan_pg_repository import MealPlanPgRepository
from user.app.use_cases.strategies.recommendation_strategy import (
    BudgetBasedRecommendationStrategy,
    RecommendationContext,
    RecommendationStrategy,
)


class MealPlanInteractor(MealPlanUseCase):
    """플랜 조회·저장 및 예산 내 맛집 추천 (Strategy 주입)."""

    def __init__(
        self,
        meal_plan_repo: IMealPlanRepository | None = None,
        budget_strategy: RecommendationStrategy | None = None,
    ) -> None:
        self._meal_plans = meal_plan_repo or MealPlanPgRepository()
        self._budget_strategy = budget_strategy or BudgetBasedRecommendationStrategy()

    def get_current_plan(
        self, db: Session, user_id: int, on_date: date | None = None
    ) -> MealPlan | None:
        plan = self._user.get_active_for_user(
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
        return self._user.save(db, plan)

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

    async def introduce_myself(self, schema) -> MealPlanIntroResponse:
        return MealPlanIntroResponse(id=schema.id, name=schema.name)
