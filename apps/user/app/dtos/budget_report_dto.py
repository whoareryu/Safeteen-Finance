from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class SetBudgetCommand:
    """월 예산 설정 (기획서 4-3)."""

    monthly_budget: int
    period_start: date
    period_end: date


@dataclass(frozen=True)
class ExpenseCommand:
    """방문 후 실제 지출 입력 (기획서 4-3)."""

    meal_plan_id: int
    amount: int
    spent_on: date
    restaurant_id: int | None = None


@dataclass(frozen=True)
class BudgetPlanView:
    meal_plan_id: int
    monthly_budget: int
    spent_amount: int
    remaining: int
    period_start: date
    period_end: date


@dataclass(frozen=True)
class BudgetReportView:
    """월말 리포트 (기획서 4-3)."""

    total_spent: int
    saved_amount: int
    top_restaurants: list[dict] = field(default_factory=list)
    top_categories: list[dict] = field(default_factory=list)
