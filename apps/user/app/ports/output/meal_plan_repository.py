from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from sqlalchemy.orm import Session

from user.adapter.outbound.orm.meal_plan_orm import MealPlan


class IMealPlanRepository(ABC):
    @abstractmethod
    def get_active_for_user(
        self, db: Session, user_id: int, on_date: date
    ) -> MealPlan | None:
        pass

    @abstractmethod
    def save(self, db: Session, plan: MealPlan) -> MealPlan:
        pass
