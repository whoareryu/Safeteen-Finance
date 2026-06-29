from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from apps.auth.user_model import User
from user.app.dtos.budget_report_dto import (
    BudgetPlanView,
    BudgetReportView,
    ExpenseCommand,
    SetBudgetCommand,
)


class BudgetReportUseCase(ABC):
    """월 예산 설정 → 지출 입력 → 잔여 차감 → 월말 리포트 (기획서 4-3)."""

    @abstractmethod
    def set_budget(
        self, db: Session, user: User, command: SetBudgetCommand
    ) -> BudgetPlanView:
        ...

    @abstractmethod
    def current_plan(self, db: Session, user_id: int) -> BudgetPlanView | None:
        ...

    @abstractmethod
    def add_expense(
        self, db: Session, user: User, command: ExpenseCommand
    ) -> BudgetPlanView:
        ...

    @abstractmethod
    def monthly_report(
        self, db: Session, user_id: int, meal_plan_id: int
    ) -> BudgetReportView:
        ...
