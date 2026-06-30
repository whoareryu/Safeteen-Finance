from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from sqlalchemy.orm import Session

from user.app.dtos.budget_report_dto import (
    BudgetPlanView,
    BudgetReportView,
    ExpenseCommand,
)


class BudgetReportRepository(ABC):
    """meal_plans + meal_plan_expenses 영속화·집계 포트."""

    @abstractmethod
    def upsert_plan(
        self,
        db: Session,
        *,
        user_id: int,
        monthly_budget: int,
        period_start: date,
        period_end: date,
        meal_type: str = "total",
    ) -> BudgetPlanView:
        ...

    @abstractmethod
    def get_active_plan(
        self, db: Session, *, user_id: int, on: date, meal_type: str = "total"
    ) -> BudgetPlanView | None:
        ...

    @abstractmethod
    def get_all_active_plans(
        self, db: Session, *, user_id: int, on: date
    ) -> list[BudgetPlanView]:
        ...

    @abstractmethod
    def add_expense(
        self, db: Session, *, user_id: int, command: ExpenseCommand
    ) -> BudgetPlanView:
        ...

    @abstractmethod
    def aggregate(
        self, db: Session, *, user_id: int, meal_plan_id: int
    ) -> BudgetReportView:
        ...
