"""MealPlan 도메인 API — Controller."""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from apps.gourmet.app.schemas.meal_plan_schemas import (
    MealPlanResponse,
    MealPlanRestaurantsResponse,
    MealPlanUpsertRequest,
)
from apps.gourmet.app.schemas.restaurant_schemas import RestaurantCardV2
from apps.gourmet.app.services.meal_plan_service import MealPlanService
from apps.gourmet.app.services.restaurant_domain_service import RestaurantDomainService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gourmet/meal-plans", tags=["gourmet-meal-plans"])

_meal_plan_service = MealPlanService()
_restaurant_presenter = RestaurantDomainService()


def _plan_response(plan) -> MealPlanResponse:
    return MealPlanResponse(
        id=plan.id,
        user_id=plan.user_id,
        monthly_budget=plan.monthly_budget,
        spent_amount=plan.spent_amount,
        period_start=plan.period_start,
        period_end=plan.period_end,
        remaining_budget=_meal_plan_service.remaining_budget(plan),
    )


@router.get("/users/{user_id}/current", response_model=MealPlanResponse)
def read_current_meal_plan(
    user_id: int,
    on: date | None = Query(None, description="기준일 (기본: 오늘)"),
    db: Session = Depends(get_sync_db),
) -> MealPlanResponse:
    plan = _meal_plan_service.get_current_plan(db, user_id, on)
    if plan is None:
        raise HTTPException(status_code=404, detail="활성 식비 플랜이 없습니다.")
    return _plan_response(plan)


@router.put("/users/{user_id}/current", response_model=MealPlanResponse)
def upsert_meal_plan(
    user_id: int,
    body: MealPlanUpsertRequest,
    db: Session = Depends(get_sync_db),
) -> MealPlanResponse:
    if body.period_end < body.period_start:
        raise HTTPException(status_code=400, detail="종료일은 시작일 이후여야 합니다.")
    plan = _meal_plan_service.upsert_plan(
        db,
        user_id=user_id,
        monthly_budget=body.monthly_budget,
        spent_amount=body.spent_amount,
        period_start=body.period_start,
        period_end=body.period_end,
    )
    return _plan_response(plan)


@router.get(
    "/users/{user_id}/restaurants",
    response_model=MealPlanRestaurantsResponse,
)
def list_restaurants_within_meal_plan(
    user_id: int,
    category_slug: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_sync_db),
) -> MealPlanRestaurantsResponse:
    rows, per_meal_cap, plan = _meal_plan_service.restaurants_within_plan(
        db,
        user_id,
        category_slug=category_slug,
        offset=offset,
        limit=limit,
    )
    cards = [RestaurantCardV2(**_restaurant_presenter.to_card_dict(r)) for r in rows]
    return MealPlanRestaurantsResponse(
        plan=_plan_response(plan) if plan else None,
        per_meal_cap=per_meal_cap,
        restaurants=cards,
        offset=offset,
        limit=limit,
    )
