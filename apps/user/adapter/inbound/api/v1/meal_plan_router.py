"""MealPlan 도메인 API — Controller."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.friday_13th.auth.dependencies import get_current_user
from apps.friday_13th.auth.user_model import User
from apps.database import get_sync_db
from user.adapter.inbound.api.schemas.meal_plan_schema import (
    MealPlanResponse,
    MealPlanRestaurantsResponse,
    MealPlanUpsertRequest,
)
from restaurant.adapter.inbound.api.schemas.restaurant_schema import RestaurantCardV2
from user.dependencies.meal_plan_provider import get_meal_plan_service
from restaurant.dependencies.restaurant_domain_provider import get_restaurant_domain_service
from user.app.ports.input.meal_plan_use_case import MealPlanUseCase
from restaurant.app.use_cases.restaurant_domain_interactor import RestaurantDomainInteractor

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
    return _plan_response(meal_plan_service.get_current_plan(db, user_id, on), meal_plan_service)


@router.put("/users/{user_id}/current", response_model=MealPlanResponse)
def upsert_meal_plan(
    user_id: int,
    body: MealPlanUpsertRequest,
    db: Session = Depends(get_sync_db),
    meal_plan_service: MealPlanUseCase = Depends(get_meal_plan_service),
) -> MealPlanResponse:
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


from user.adapter.inbound.api.schemas.meal_plan_schema import MealPlanSchema
from user.app.dtos.meal_plan_dto import MealPlanIntroResponse


@router.get("/myself")
async def introduce_meal_plan(
    use_case: MealPlanUseCase = Depends(get_meal_plan_service),
) -> MealPlanIntroResponse:
    return await use_case.introduce_myself(MealPlanSchema(id=1, name="식비 계획"))
