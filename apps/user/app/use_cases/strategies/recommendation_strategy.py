"""추천 Strategy — 예산·카테고리 등 알고리즘 다형성."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from user.adapter.outbound.orm.meal_plan_orm import MealPlan
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.pg.interfaces import IRestaurantRepository
from restaurant.adapter.outbound.pg.restaurant_pg_repository import RestaurantRepository


@dataclass(frozen=True, slots=True)
class RecommendationContext:
    """전략 실행 입력 — Controller/Service 가 조립."""

    offset: int = 0
    limit: int = 20
    category_slug: str | None = None
    district: str | None = None
    meal_plan: MealPlan | None = None
    on_date: date | None = None


@dataclass(frozen=True, slots=True)
class RecommendationResult:
    restaurants: list[Restaurant]
    meta_cap: int = 0


class RecommendationStrategy(ABC):
    """GOF Strategy — ``recommend`` 로 구현체 교체."""

    @abstractmethod
    def recommend(
        self, db: Session, ctx: RecommendationContext
    ) -> RecommendationResult:
        raise NotImplementedError


class BudgetBasedRecommendationStrategy(RecommendationStrategy):
    """식비 플랜 잔여 예산 → 1끼 상한 → ``avg_price`` 필터."""

    def __init__(self, restaurant_repo: IRestaurantRepository | None = None) -> None:
        self._restaurants = restaurant_repo or RestaurantRepository()

    @staticmethod
    def per_meal_cap(plan: MealPlan, on_date: date) -> int:
        remaining = max(0, plan.monthly_budget - plan.spent_amount)
        days_left = max(1, (plan.period_end - on_date).days + 1)
        return max(3_000, remaining // days_left)

    def recommend(
        self, db: Session, ctx: RecommendationContext
    ) -> RecommendationResult:
        if ctx.meal_plan is None:
            return RecommendationResult(restaurants=[], meta_cap=0)
        today = ctx.on_date or date.today()
        cap = self.per_meal_cap(ctx.meal_plan, today)
        rows = self._restaurant.list_within_budget(
            db,
            max_avg_price=cap,
            category_slug=ctx.category_slug,
            offset=ctx.offset,
            limit=ctx.limit,
        )
        return RecommendationResult(restaurants=rows, meta_cap=cap)


class CategoryBrowseRecommendationStrategy(RecommendationStrategy):
    """카테고리 탭 목록 (v2 API)."""

    def __init__(self, restaurant_repo: IRestaurantRepository | None = None) -> None:
        self._restaurants = restaurant_repo or RestaurantRepository()

    def recommend(
        self, db: Session, ctx: RecommendationContext
    ) -> RecommendationResult:
        if not ctx.category_slug:
            return RecommendationResult(restaurants=[])
        rows = self._restaurant.list_by_category(
            db,
            category_slug=ctx.category_slug,
            offset=ctx.offset,
            limit=ctx.limit,
            district=ctx.district,
        )
        return RecommendationResult(restaurants=rows)
