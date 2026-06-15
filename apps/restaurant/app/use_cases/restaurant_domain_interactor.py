"""Restaurant 도메인 — Repository·Strategy·엔티티 캡슐화."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.app.ports.input.restaurant_use_case import RestaurantUseCase
from restaurant.app.ports.output.restaurant_repository import IRestaurantRepository
from restaurant.adapter.outbound.pg.restaurant_pg_repository import RestaurantRepository
from restaurant.adapter.inbound.api.schemas.restaurant_domain_schema import RestaurantDomainSchema
from restaurant.app.dtos.restaurant_domain_dto import RestaurantDomainQuery, RestaurantDomainResponse
from restaurant.app.ports.output.restaurant_domain_repository import RestaurantDomainRepository
from user.app.use_cases.strategies.recommendation_strategy import (
    CategoryBrowseRecommendationStrategy,
    RecommendationContext,
)


class RestaurantDomainInteractor(RestaurantUseCase):
    def __init__(
        self,
        repository: IRestaurantRepository | None = None,
        browse_strategy: CategoryBrowseRecommendationStrategy | None = None,
    ) -> None:
        self._repo = repository or RestaurantRepository()
        self._browse_strategy = browse_strategy or CategoryBrowseRecommendationStrategy(
            restaurant_repo=self._repo
        )

    def get_detail(self, db: Session, restaurant_id: int) -> Restaurant | None:
        return self._repo.get_by_id(db, restaurant_id)

    def list_category_page(
        self,
        db: Session,
        *,
        category_slug: str,
        offset: int,
        limit: int,
        district: str | None = None,
    ) -> tuple[list[Restaurant], int]:
        ctx = RecommendationContext(
            offset=offset,
            limit=limit,
            category_slug=category_slug,
            district=district,
        )
        result = self._browse_strategy.recommend(db, ctx)
        total = self._repo.count_by_category(
            db, category_slug=category_slug, district=district
        )
        return result.restaurants, total

    @staticmethod
    def to_card_dict(row: Restaurant, **kwargs: Any) -> dict[str, Any]:
        return row.to_card_dict(**kwargs)

    async def introduce_myself(self, schema: RestaurantDomainSchema) -> RestaurantDomainResponse:
        return RestaurantDomainResponse(id=schema.id, name=schema.name)
