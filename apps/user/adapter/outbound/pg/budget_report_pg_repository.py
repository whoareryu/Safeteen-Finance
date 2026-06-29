from __future__ import annotations

from datetime import date

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from user.adapter.outbound.orm.meal_plan_expense_orm import MealPlanExpense
from user.adapter.outbound.orm.meal_plan_orm import MealPlan
from user.app.dtos.budget_report_dto import (
    BudgetPlanView,
    BudgetReportView,
    ExpenseCommand,
)
from user.app.ports.output.budget_report_repository import BudgetReportRepository


class BudgetReportPgRepository(BudgetReportRepository):
    @staticmethod
    def _view(plan: MealPlan) -> BudgetPlanView:
        return BudgetPlanView(
            meal_plan_id=plan.id,
            monthly_budget=plan.monthly_budget,
            spent_amount=plan.spent_amount,
            remaining=max(0, plan.monthly_budget - plan.spent_amount),
            period_start=plan.period_start,
            period_end=plan.period_end,
        )

    def _active(self, db: Session, user_id: int, on: date) -> MealPlan | None:
        stmt = (
            select(MealPlan)
            .where(
                MealPlan.user_id == user_id,
                MealPlan.period_start <= on,
                MealPlan.period_end >= on,
            )
            .order_by(MealPlan.id.desc())
            .limit(1)
        )
        return db.scalars(stmt).first()

    def upsert_plan(
        self,
        db: Session,
        *,
        user_id: int,
        monthly_budget: int,
        period_start: date,
        period_end: date,
    ) -> BudgetPlanView:
        plan = self._active(db, user_id, period_start)
        if plan is None:
            plan = MealPlan(
                user_id=user_id,
                monthly_budget=monthly_budget,
                spent_amount=0,
                period_start=period_start,
                period_end=period_end,
            )
            db.add(plan)
        else:
            plan.monthly_budget = monthly_budget
            plan.period_start = period_start
            plan.period_end = period_end
        db.commit()
        db.refresh(plan)
        return self._view(plan)

    def get_active_plan(
        self, db: Session, *, user_id: int, on: date
    ) -> BudgetPlanView | None:
        plan = self._active(db, user_id, on)
        return self._view(plan) if plan else None

    def add_expense(
        self, db: Session, *, user_id: int, command: ExpenseCommand
    ) -> BudgetPlanView:
        plan = db.get(MealPlan, command.meal_plan_id)
        if plan is None or plan.user_id != user_id:
            raise ValueError("식비 플랜을 찾을 수 없습니다.")
        db.add(
            MealPlanExpense(
                user_id=user_id,
                meal_plan_id=command.meal_plan_id,
                restaurant_id=command.restaurant_id,
                amount=command.amount,
                spent_on=command.spent_on,
            )
        )
        plan.spent_amount = (plan.spent_amount or 0) + command.amount
        db.commit()
        db.refresh(plan)
        return self._view(plan)

    def aggregate(
        self, db: Session, *, user_id: int, meal_plan_id: int
    ) -> BudgetReportView:
        plan = db.get(MealPlan, meal_plan_id)
        if plan is None or plan.user_id != user_id:
            raise ValueError("식비 플랜을 찾을 수 없습니다.")
        params = {"mp": meal_plan_id, "u": user_id}
        total = (
            db.execute(
                text(
                    "SELECT COALESCE(SUM(amount),0) FROM meal_plan_expenses "
                    "WHERE meal_plan_id=:mp AND user_id=:u"
                ),
                params,
            ).scalar()
            or 0
        )
        top_restaurants = db.execute(
            text(
                "SELECT r.name AS name, SUM(e.amount) AS total, COUNT(*) AS visits "
                "FROM meal_plan_expenses e JOIN restaurants r ON e.restaurant_id=r.id "
                "WHERE e.meal_plan_id=:mp AND e.user_id=:u "
                "GROUP BY r.id, r.name ORDER BY total DESC LIMIT 5"
            ),
            params,
        ).mappings().all()
        top_categories = db.execute(
            text(
                "SELECT fc.label AS label, SUM(e.amount) AS total, COUNT(*) AS visits "
                "FROM meal_plan_expenses e JOIN restaurants r ON e.restaurant_id=r.id "
                "JOIN food_categories fc ON r.category_id=fc.id "
                "WHERE e.meal_plan_id=:mp AND e.user_id=:u "
                "GROUP BY fc.label ORDER BY total DESC LIMIT 5"
            ),
            params,
        ).mappings().all()
        return BudgetReportView(
            total_spent=int(total),
            saved_amount=max(0, plan.monthly_budget - int(total)),
            top_restaurants=[dict(row) for row in top_restaurants],
            top_categories=[dict(row) for row in top_categories],
        )
