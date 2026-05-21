"""Repository 계약 (Protocol) — Service 계층은 구현체가 아닌 인터페이스에 의존."""

from __future__ import annotations

from datetime import date
from typing import Protocol

from sqlalchemy.orm import Session

from apps.gourmet.app.models.meal_plan import MealPlan
from apps.gourmet.app.models.restaurant import Restaurant


class IRestaurantRepository(Protocol):
    def get_by_id(self, db: Session, restaurant_id: int) -> Restaurant | None: ...

    def bulk_insert(
        self, db: Session, rows: list[Restaurant], *, commit: bool = True
    ) -> int: ...

    def delete_all(self, db: Session) -> int: ...

    def list_by_category(
        self,
        db: Session,
        *,
        category_slug: str,
        offset: int,
        limit: int,
        district: str | None = None,
    ) -> list[Restaurant]: ...

    def list_within_budget(
        self,
        db: Session,
        *,
        max_avg_price: int,
        category_slug: str | None,
        offset: int,
        limit: int,
    ) -> list[Restaurant]: ...

    def count_by_category(
        self, db: Session, *, category_slug: str, district: str | None = None
    ) -> int: ...


class IMealPlanRepository(Protocol):
    def get_active_for_user(
        self, db: Session, user_id: int, on_date: date
    ) -> MealPlan | None: ...

    def save(self, db: Session, plan: MealPlan) -> MealPlan: ...
