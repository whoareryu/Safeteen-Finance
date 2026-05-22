"""Restaurant 도메인 — Repository·Strategy·엔티티 캡슐화."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from apps.gourmet.app.data.ingestion.csv_restaurant_importer import CsvRestaurantImporter
from apps.gourmet.app.models.restaurant import Restaurant
from apps.gourmet.app.repositories.interfaces import IRestaurantRepository
from apps.gourmet.app.repositories.restaurant_repository import RestaurantRepository
from apps.gourmet.app.services.strategies.recommendation_strategy import (
    CategoryBrowseRecommendationStrategy,
    RecommendationContext,
)


class RestaurantDomainService:
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

    def import_from_csv(
        self,
        db: Session,
        csv_path: Path,
        *,
        replace_all: bool = True,
    ) -> tuple[int, int]:
        importer = CsvRestaurantImporter(repository=self._repo)  # type: ignore[arg-type]
        return importer.import_file(db, csv_path, replace_all=replace_all)

    @staticmethod
    def to_card_dict(row: Restaurant, **kwargs: Any) -> dict[str, Any]:
        return row.to_card_dict(**kwargs)
