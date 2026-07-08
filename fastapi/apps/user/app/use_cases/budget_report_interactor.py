from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from apps.auth.user_model import User
from user.app.dtos.budget_report_dto import (
    BudgetPlanView,
    BudgetReportView,
    ExpenseCommand,
    SetBudgetCommand,
)
from user.app.ports.input.budget_report_use_case import BudgetReportUseCase
from user.app.ports.output.budget_report_repository import BudgetReportRepository


class BudgetReportInteractor(BudgetReportUseCase):
    def __init__(self, repository: BudgetReportRepository) -> None:
        self._repository = repository

    def set_budget(
        self, db: Session, user: User, command: SetBudgetCommand
    ) -> BudgetPlanView:
        return self._repository.upsert_plan(
            db,
            user_id=user.id,
            monthly_budget=command.monthly_budget,
            period_start=command.period_start,
            period_end=command.period_end,
            meal_type=command.meal_type,
        )

    def current_plan(self, db: Session, user_id: int) -> BudgetPlanView | None:
        return self._repository.get_active_plan(db, user_id=user_id, on=date.today())

    def all_plans(self, db: Session, user_id: int) -> list[BudgetPlanView]:
        return self._repository.get_all_active_plans(db, user_id=user_id, on=date.today())

    def add_expense(
        self, db: Session, user: User, command: ExpenseCommand
    ) -> BudgetPlanView:
        return self._repository.add_expense(db, user_id=user.id, command=command)

    def monthly_report(
        self, db: Session, user_id: int, meal_plan_id: int
    ) -> BudgetReportView:
        return self._repository.aggregate(
            db, user_id=user_id, meal_plan_id=meal_plan_id
        )
