from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class SetBudgetRequest(BaseModel):
    monthly_budget: int = Field(..., ge=0)
    period_start: date
    period_end: date
    meal_type: str = "total"  # total / morning / lunch / dinner


class ExpenseRequest(BaseModel):
    meal_plan_id: int
    amount: int = Field(..., ge=0)
    spent_on: date
    restaurant_id: int | None = None


class BudgetPlanResponse(BaseModel):
    meal_plan_id: int
    monthly_budget: int
    spent_amount: int
    remaining: int
    period_start: date
    period_end: date
    meal_type: str = "total"


class BudgetReportResponse(BaseModel):
    total_spent: int
    saved_amount: int
    top_restaurants: list[dict] = Field(default_factory=list)
    top_categories: list[dict] = Field(default_factory=list)
