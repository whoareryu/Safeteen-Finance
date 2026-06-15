"""오늘의 추천 맛집 — 하루 1곳, 버짓설정 시 일일 식비 반영."""

from __future__ import annotations

import random
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from restaurant.data.ingestion.category_normalizer import (
    NON_MEAL_CATEGORY_SLUGS,
    is_meal_category_slug,
)
from restaurant.adapter.outbound.orm.daily_recommendation_orm import DailyRecommendation
from user.adapter.outbound.orm.meal_plan_orm import MealPlan
from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.orm.restaurant_price_orm import RestaurantPrice
from restaurant.adapter.outbound.pg.restaurant_orm_loads import RESTAURANT_CARD_LOADS
from user.adapter.outbound.pg.meal_plan_pg_repository import MealPlanPgRepository
from restaurant.app.use_cases.restaurant_location_interactor import distance_km_to_entity
from restaurant.app.use_cases.restaurant_browse_interactor import (
from restaurant.app.ports.input.daily_pick_use_case import DailyPickUseCase
from restaurant.adapter.inbound.api.schemas.daily_pick_schema import DailyPickSchema
from restaurant.app.dtos.daily_pick_dto import DailyPickQuery, DailyPickResponse
from restaurant.app.ports.output.daily_pick_repository import DailyPickRepository

    RestaurantBrowseRow,
    bounded_restaurant_slice,
    browse_category_of,
    rows_to_card_summaries,
)


def daily_allowance_from_plan(plan: MealPlan) -> int:
    """기간 목표 식비 ÷ 기간 일수 = 하루 권장 사용액."""
    period_days = max(1, (plan.period_end - plan.period_start).days + 1)
    return max(3_000, plan.monthly_budget // period_days)


def _meal_only_restaurant_clause():
    return FoodCategory.slug.notin_(tuple(NON_MEAL_CATEGORY_SLUGS))


def _pick_restaurant_by_seed(
    db: Session,
    *,
    seed: int,
    max_avg_price: int | None,
) -> Restaurant | None:
    def _count_where(price_cap: int | None) -> int:
        stmt = (
            select(func.count())
            .select_from(Restaurant)
            .join(FoodCategory, Restaurant.category_id == FoodCategory.id)
            .where(_meal_only_restaurant_clause())
        )
        if price_cap is not None:
            stmt = stmt.join(
                RestaurantPrice, RestaurantPrice.restaurant_id == Restaurant.id
            ).where(
                RestaurantPrice.avg_price.is_not(None),
                RestaurantPrice.avg_price <= price_cap,
            )
        return int(db.execute(stmt).scalar_one() or 0)

    def _fetch_at_offset(price_cap: int | None, offset: int) -> Restaurant | None:
        stmt = (
            select(Restaurant)
            .options(*RESTAURANT_CARD_LOADS)
            .join(FoodCategory, Restaurant.category_id == FoodCategory.id)
            .where(_meal_only_restaurant_clause())
        )
        if price_cap is not None:
            stmt = stmt.join(
                RestaurantPrice, RestaurantPrice.restaurant_id == Restaurant.id
            ).where(
                RestaurantPrice.avg_price.is_not(None),
                RestaurantPrice.avg_price <= price_cap,
            )
        return db.scalars(
            stmt.order_by(Restaurant.id).offset(offset).limit(1)
        ).unique().first()

    cap = max_avg_price
    count = _count_where(cap)
    if count == 0 and cap is not None:
        cap = None
        count = _count_where(None)
    if count == 0:
        return None
    offset = random.Random(seed).randrange(count)
    return _fetch_at_offset(cap, offset)


def _existing_daily_rec(
    db: Session, user_id: int, on_date: date
) -> DailyRecommendation | None:
    return db.execute(
        select(DailyRecommendation)
        .where(
            DailyRecommendation.user_id == user_id,
            DailyRecommendation.recommended_on == on_date,
        )
        .limit(1)
    ).scalar_one_or_none()


def get_daily_pick(
    db: Session,
    *,
    on_date: date | None = None,
    user_id: int | None = None,
    user_lat: float | None = None,
    user_lng: float | None = None,
) -> dict:
    today = on_date or date.today()
    daily_budget: int | None = None
    budget_applied = False
    message = "오늘 하루, 이곳 어떠세요?"

    meal_plan: MealPlan | None = None
    if user_id is not None:
        meal_plan = MealPlanPgRepository().get_active_for_user(db, user_id, today)

    if meal_plan is not None:
        daily_budget = daily_allowance_from_plan(meal_plan)
        budget_applied = True
        message = (
            f"버짓설정 기준 하루 권장 식비 {daily_budget:,}원 이하 매장을 골랐습니다."
        )

    existing = None
    if user_id is not None:
        existing = _existing_daily_rec(db, user_id, today)
        if existing is not None:
            r = db.scalars(
                select(Restaurant)
                .where(Restaurant.id == existing.restaurant_id)
                .options(*RESTAURANT_CARD_LOADS)
            ).first()
            if r is not None and is_meal_category_slug(r.category_slug):
                return _build_response(
                    db, r, today, daily_budget, budget_applied, message, user_lat, user_lng
                )

    seed = today.toordinal() + (user_id or 0)
    max_price = daily_budget if budget_applied else None
    picked = _pick_restaurant_by_seed(db, seed=seed, max_avg_price=max_price)

    if picked is None:
        row = _fallback_browse_pick(db, today, user_lat, user_lng)
        if row is None:
            return {
                "date": today.isoformat(),
                "restaurant": None,
                "daily_budget": daily_budget,
                "budget_applied": budget_applied,
                "message": "추천할 매장을 찾지 못했습니다.",
            }
        return {
            "date": today.isoformat(),
            "restaurant": row,
            "daily_budget": daily_budget,
            "budget_applied": budget_applied,
            "message": message,
        }

    if user_id is not None:
        if existing is not None:
            existing.restaurant_id = picked.id
            existing.meal_plan_id = meal_plan.id if meal_plan else None
            existing.pick_reason = message[:500]
        else:
            db.add(
                DailyRecommendation(
                    user_id=user_id,
                    restaurant_id=picked.id,
                    meal_plan_id=meal_plan.id if meal_plan else None,
                    recommended_on=today,
                    pick_reason=message[:500],
                )
            )
        try:
            db.commit()
        except Exception:
            db.rollback()

    return _build_response(
        db, picked, today, daily_budget, budget_applied, message, user_lat, user_lng
    )


def _build_response(
    db: Session,
    r: Restaurant,
    today: date,
    daily_budget: int | None,
    budget_applied: bool,
    message: str,
    user_lat: float | None,
    user_lng: float | None,
) -> dict:
    store_id = r.id
    dist = None
    if user_lat is not None and user_lng is not None:
        dist = distance_km_to_entity(r, user_lat, user_lng)
    return {
        "date": today.isoformat(),
        "restaurant": {
            "id": store_id,
            "name": r.display_name(),
            "image_url": r.image_url or "",
            "district": r.district or "",
            "category_slug": r.category_slug,
            "category_label": r.category_label,
            "avg_price": r.avg_price,
            "signature_menu": r.signature_menu or "",
            "distance_km": dist,
        },
        "daily_budget": daily_budget,
        "budget_applied": budget_applied,
        "message": message,
    }


def _fallback_browse_pick(
    db: Session,
    today: date,
    user_lat: float | None,
    user_lng: float | None,
) -> dict | None:
    rows = bounded_restaurant_slice(
        db, limit_rows=8000, rotation_salt=0, day_ord=today.toordinal()
    )
    meal_rows = [
        r for r in rows if is_meal_category_slug(browse_category_of(r)[0])
    ]
    if not meal_rows:
        return None
    rng = random.Random(today.toordinal())
    one: RestaurantBrowseRow = rng.choice(meal_rows)
    cards = rows_to_card_summaries(
        [one], user_lat=user_lat, user_lng=user_lng, with_category=True
    )
    if not cards:
        return None
    c = cards[0]
    return {
        "id": c["id"],
        "name": c["name"],
        "image_url": c.get("image_url", ""),
        "district": c.get("district", ""),
        "category_slug": c.get("category_slug"),
        "category_label": c.get("category_label"),
        "avg_price": None,
        "signature_menu": "",
        "distance_km": c.get("distance_km"),
    }


class DailyPickInteractor(DailyPickUseCase):
    def __init__(self, repository: DailyPickRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: DailyPickSchema) -> DailyPickResponse:
        return await self.repository.introduce_myself(
            DailyPickQuery(id=schema.id, name=schema.name)
        )
