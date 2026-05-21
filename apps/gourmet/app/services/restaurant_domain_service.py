"""Restaurant 도메인 비즈니스 로직 (v2 API·적재)."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from apps.gourmet.app.data.ingestion.csv_restaurant_importer import CsvRestaurantImporter
from apps.gourmet.app.models.restaurant import Restaurant
from apps.gourmet.app.repositories.interfaces import IRestaurantRepository
from apps.gourmet.app.repositories.restaurant_repository import RestaurantRepository


class RestaurantDomainService:
    def __init__(self, repository: IRestaurantRepository | None = None) -> None:
        self._repo = repository or RestaurantRepository()

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
        rows = self._repo.list_by_category(
            db,
            category_slug=category_slug,
            offset=offset,
            limit=limit,
            district=district,
        )
        total = self._repo.count_by_category(
            db, category_slug=category_slug, district=district
        )
        return rows, total

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
    def to_card_dict(row: Restaurant) -> dict:
        return {
            "id": row.id,
            "name": row.name,
            "image_url": row.image_url,
            "district": row.district,
            "category_slug": row.category_slug,
            "category_label": row.category_label,
            "avg_price": row.avg_price,
            "signature_menu": row.signature_menu,
            "ai_tags": row.ai_tags or [],
        }
