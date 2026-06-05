"""MealPlan 도메인 API — Controller."""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.friday_13th.auth.dependencies import get_current_user
from apps.friday_13th.auth.user_model import User
from apps.database import get_sync_db
from gourmet.adapter.inbound.api.schemas.meal_plan_schemas import (
    MealPlanResponse,
    MealPlanRestaurantsResponse,
    MealPlanUpsertRequest,
)
from gourmet.adapter.inbound.api.schemas.restaurant_schemas import RestaurantCardV2
from gourmet.dependencies import (
    get_meal_plan_service,
    get_restaurant_domain_service,
)
from gourmet.app.ports.input.meal_plan_use_case import MealPlanUseCase
from gourmet.app.use_cases.restaurant_domain_interactor import RestaurantDomainInteractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gourmet/meal-plans", tags=["gourmet-meal-plans"])


def _plan_response(plan, meal_plan_service: MealPlanUseCase) -> MealPlanResponse:
    return MealPlanResponse(
        id=plan.id,
        user_id=plan.user_id,
        monthly_budget=plan.monthly_budget,
        spent_amount=plan.spent_amount,
        period_start=plan.period_start,
        period_end=plan.period_end,
        remaining_budget=meal_plan_service.remaining_budget(plan),
    )


@router.get("/me/current", response_model=MealPlanResponse)
def read_my_meal_plan(
    on: date | None = Query(None, description="기준일 (기본: 오늘)"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    meal_plan_service: MealPlanUseCase = Depends(get_meal_plan_service),
) -> MealPlanResponse:
    return read_current_meal_plan(user.id, on, db, meal_plan_service)


@router.put("/me/current", response_model=MealPlanResponse)
def upsert_my_meal_plan(
    body: MealPlanUpsertRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
    meal_plan_service: MealPlanUseCase = Depends(get_meal_plan_service),
) -> MealPlanResponse:
    return upsert_meal_plan(user.id, body, db, meal_plan_service)


@router.get("/users/{user_id}/current", response_model=MealPlanResponse)
def read_current_meal_plan(
    user_id: int,
    on: date | None = Query(None, description="기준일 (기본: 오늘)"),
    db: Session = Depends(get_sync_db),
    meal_plan_service: MealPlanUseCase = Depends(get_meal_plan_service),
) -> MealPlanResponse:
    plan = meal_plan_service.get_current_plan(db, user_id, on)
    if plan is None:
        raise HTTPException(status_code=404, detail="활성 식비 플랜이 없습니다.")
    return _plan_response(plan, meal_plan_service)


@router.put("/users/{user_id}/current", response_model=MealPlanResponse)
def upsert_meal_plan(
    user_id: int,
    body: MealPlanUpsertRequest,
    db: Session = Depends(get_sync_db),
    meal_plan_service: MealPlanUseCase = Depends(get_meal_plan_service),
) -> MealPlanResponse:
    if body.period_end < body.period_start:
        raise HTTPException(status_code=400, detail="종료일은 시작일 이후여야 합니다.")
    plan = meal_plan_service.upsert_plan(
        db,
        user_id=user_id,
        monthly_budget=body.monthly_budget,
        spent_amount=body.spent_amount,
        period_start=body.period_start,
        period_end=body.period_end,
    )
    return _plan_response(plan, meal_plan_service)


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
    meal_plan_service: MealPlanUseCase = Depends(get_meal_plan_service),
    restaurant_service: RestaurantDomainInteractor = Depends(get_restaurant_domain_service),
) -> MealPlanRestaurantsResponse:
    rows, per_meal_cap, plan = meal_plan_service.restaurants_within_plan(
        db,
        user_id,
        category_slug=category_slug,
        offset=offset,
        limit=limit,
    )
    cards = [
        RestaurantCardV2(**restaurant_service.to_card_dict(r)) for r in rows
    ]
    return MealPlanRestaurantsResponse(
        plan=_plan_response(plan, meal_plan_service) if plan else None,
        per_meal_cap=per_meal_cap,
        restaurants=cards,
        offset=offset,
        limit=limit,
    )
