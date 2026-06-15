"""``meal_plans`` 테이블 접근."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from user.adapter.outbound.orm.meal_plan_orm import MealPlan
from restaurant.adapter.outbound.pg.base_pg_repository import AbstractRepository
from user.app.ports.output.meal_plan_repository import IMealPlanRepository


class MealPlanPgRepository(AbstractRepository[MealPlan], IMealPlanRepository):
    def get_by_id(self, db: Session, entity_id: int) -> MealPlan | None:
        return db.get(MealPlan, entity_id)

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
