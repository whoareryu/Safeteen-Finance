"""``meal_plans`` 테이블 접근."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.gourmet.app.models.meal_plan import MealPlan
from apps.gourmet.app.repositories.interfaces import IMealPlanRepository


class MealPlanRepository:
    """``IMealPlanRepository`` 구현."""

    def get_active_for_user(
        self, db: Session, user_id: int, on_date: date
    ) -> MealPlan | None:
        stmt = (
            select(MealPlan)
            .where(MealPlan.user_id == user_id)
            .where(MealPlan.period_start <= on_date)
            .where(MealPlan.period_end >= on_date)
            .order_by(MealPlan.id.desc())
            .limit(1)
        )
        return db.scalars(stmt).first()

    def save(self, db: Session, plan: MealPlan) -> MealPlan:
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan
