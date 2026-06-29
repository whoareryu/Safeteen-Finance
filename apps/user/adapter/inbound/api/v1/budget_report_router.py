"""버짓(식비) API — X-User-Id 인증 (기획서 4-3)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.auth.dependencies import get_current_user
from apps.auth.user_model import User
from apps.database import get_sync_db
from user.adapter.inbound.api.schemas.budget_report_schema import (
    BudgetPlanResponse,
    BudgetReportResponse,
    ExpenseRequest,
    SetBudgetRequest,
)
from user.app.dtos.budget_report_dto import (
    BudgetPlanView,
    ExpenseCommand,
    SetBudgetCommand,
)
from user.app.ports.input.budget_report_use_case import BudgetReportUseCase
from user.dependencies.budget_report_provider import get_budget_report_use_case

budget_report_router = APIRouter(prefix="/gourmet/budget", tags=["gourmet-budget"])
router = budget_report_router


def _plan_response(view: BudgetPlanView) -> BudgetPlanResponse:
    return BudgetPlanResponse(
        meal_plan_id=view.meal_plan_id,
        monthly_budget=view.monthly_budget,
        spent_amount=view.spent_amount,
        remaining=view.remaining,
        period_start=view.period_start,
        period_end=view.period_end,
    )


@budget_report_router.get("/plan", response_model=BudgetPlanResponse | None)
def read_plan(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    use_case: BudgetReportUseCase = Depends(get_budget_report_use_case),
) -> BudgetPlanResponse | None:
    view = use_case.current_plan(db, user.id)
    return _plan_response(view) if view else None


@budget_report_router.put("/plan", response_model=BudgetPlanResponse)
def set_budget(
    body: SetBudgetRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    use_case: BudgetReportUseCase = Depends(get_budget_report_use_case),
) -> BudgetPlanResponse:
    view = use_case.set_budget(
        db,
        user,
        SetBudgetCommand(
            monthly_budget=body.monthly_budget,
            period_start=body.period_start,
            period_end=body.period_end,
        ),
    )
    return _plan_response(view)


@budget_report_router.post("/expense", response_model=BudgetPlanResponse)
def add_expense(
    body: ExpenseRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    use_case: BudgetReportUseCase = Depends(get_budget_report_use_case),
) -> BudgetPlanResponse:
    try:
        view = use_case.add_expense(
            db,
            user,
            ExpenseCommand(
                meal_plan_id=body.meal_plan_id,
                amount=body.amount,
                spent_on=body.spent_on,
                restaurant_id=body.restaurant_id,
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _plan_response(view)


@budget_report_router.get("/report", response_model=BudgetReportResponse)
def read_report(
    meal_plan_id: int = Query(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    use_case: BudgetReportUseCase = Depends(get_budget_report_use_case),
) -> BudgetReportResponse:
    try:
        report = use_case.monthly_report(db, user.id, meal_plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return BudgetReportResponse(
        total_spent=report.total_spent,
        saved_amount=report.saved_amount,
        top_restaurants=report.top_restaurants,
        top_categories=report.top_categories,
    )
