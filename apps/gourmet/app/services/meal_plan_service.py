"""식비 플랜 — 잔여 예산 범위 내 식당 필터."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from apps.gourmet.app.models.meal_plan import MealPlan
from apps.gourmet.app.models.restaurant import Restaurant
from apps.gourmet.app.repositories.interfaces import IMealPlanRepository, IRestaurantRepository
from apps.gourmet.app.repositories.meal_plan_repository import MealPlanRepository
from apps.gourmet.app.repositories.restaurant_repository import RestaurantRepository


class MealPlanService:
    """플랜 조회·저장 및 예산 내 맛집 추천 풀."""

    def __init__(
        self,
        meal_plan_repo: IMealPlanRepository | None = None,
        restaurant_repo: IRestaurantRepository | None = None,
    ) -> None:
        self._meal_plans = meal_plan_repo or MealPlanRepository()
        self._restaurants = restaurant_repo or RestaurantRepository()

    def get_current_plan(
        self, db: Session, user_id: int, on_date: date | None = None
    ) -> MealPlan | None:
        return self._meal_plans.get_active_for_user(
            db, user_id, on_date or date.today()
        )

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
        """1회 식사 추정 상한 = 잔여 예산 / 남은 일수 (최소 1일)."""
        plan = self.get_current_plan(db, user_id, on_date)
        if plan is None:
            return [], 0, None

        remaining = self.remaining_budget(plan)
        today = on_date or date.today()
        days_left = max(1, (plan.period_end - today).days + 1)
        per_meal_cap = max(3_000, remaining // days_left)

        rows = self._restaurants.list_within_budget(
            db,
            max_avg_price=per_meal_cap,
            category_slug=category_slug,
            offset=offset,
            limit=limit,
        )
        return rows, per_meal_cap, plan
