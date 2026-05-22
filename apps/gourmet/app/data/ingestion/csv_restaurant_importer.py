"""공공 CSV → ``restaurants`` 테이블 (Template Method 구현체)."""

from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy.orm import Session

from apps.gourmet.app.data.ingestion.base_restaurant_importer import BaseRestaurantImporter
from apps.gourmet.app.data.ingestion.restaurant_row_cleaner import RestaurantCsvRowCleaner
from apps.gourmet.app.models.restaurant import Restaurant
from apps.gourmet.app.models.restaurant_menu import RestaurantMenu
from apps.gourmet.app.models.restaurant_price import RestaurantPrice
from apps.gourmet.app.models.restaurant_tag import RestaurantTag
from apps.gourmet.app.repositories.food_category_repository import FoodCategoryRepository
from apps.gourmet.app.repositories.master_lookup_repository import (
    BizClassificationRepository,
    SigunguDistrictRepository,
    TagRepository,
)
from apps.gourmet.app.repositories.restaurant_repository import RestaurantRepository


class CsvRestaurantImporter(BaseRestaurantImporter):
    """CSV 소스 Adapter + Template Method ``import_file``."""

    def __init__(
        self,
        *,
        cleaner: RestaurantCsvRowCleaner | None = None,
        repository: RestaurantRepository | None = None,
        chunk_size: int = 1000,
    ) -> None:
        super().__init__(repository or RestaurantRepository(), chunk_size=chunk_size)
        self._cleaner = cleaner or RestaurantCsvRowCleaner()
        self._category_ids: dict[str, int] = {}
        self._sigungu_cache: dict[tuple[str, str], int] = {}
        self._biz_cache: dict[tuple[str, str, str], int] = {}
        self._tag_cache: dict[str, int] = {}
        self._db: Session | None = None

    def import_file(
        self, db: Session, source: Path, *, replace_all: bool = True
    ) -> tuple[int, int]:
        self._category_ids = FoodCategoryRepository().ensure_seeded(db)
        self._sigungu_cache.clear()
        self._biz_cache.clear()
        self._tag_cache.clear()
        self._db = db
        try:
            return super().import_file(db, source, replace_all=replace_all)
        finally:
            self._db = None

    def _sigungu_id(self, db: Session, sigungu_name: str, district: str) -> int:
        key = (sigungu_name, district)
        if key not in self._sigungu_cache:
            self._sigungu_cache[key] = SigunguDistrictRepository().get_or_create_id(
                db, sigungu_name=sigungu_name, district_label=district
            )
        return self._sigungu_cache[key]

    def _biz_id(
        self, db: Session, biz_mid: str, biz_minor: str, ksic: str
    ) -> int:
        key = (biz_mid, biz_minor, ksic)
        if key not in self._biz_cache:
            self._biz_cache[key] = BizClassificationRepository().get_or_create_id(
                db,
                biz_mid_name=biz_mid,
                biz_minor_name=biz_minor,
                ksic_name=ksic,
            )
        return self._biz_cache[key]

    def _tag_links(self, db: Session, labels: list) -> list[RestaurantTag]:
        links: list[RestaurantTag] = []
        for label in labels or []:
            text = str(label).strip()
            if not text:
                continue
            if text not in self._tag_cache:
                self._tag_cache[text] = TagRepository().get_or_create_id(db, text)
            links.append(RestaurantTag(tag_id=self._tag_cache[text]))
        return links

    def _iter_entities(self, source: Path):
        seen_biz: set[str] = set()
        with source.open(encoding="utf-8-sig", newline="") as f:
            for raw in csv.DictReader(f):
                biz = (raw.get("상가업소번호") or "").strip()
                if not biz or biz in seen_biz:
                    yield None
                    continue
                cleaned = self._cleaner.clean(raw)
                if cleaned is None:
                    yield None
                    continue
                seen_biz.add(cleaned.biz_number)
                cat_id = self._category_ids.get(cleaned.category_slug)
                if cat_id is None:
                    yield None
                    continue
                yield self._build_entity(self._db, cleaned, cat_id)

    def _build_entity(self, db: Session, cleaned, cat_id: int) -> Restaurant:
        entity = Restaurant(
            biz_number=cleaned.biz_number,
            name=cleaned.name,
            store_name=cleaned.store_name,
            branch_name=cleaned.branch_name,
            category_id=cat_id,
            sigungu_id=self._sigungu_id(db, cleaned.sigungu_name, cleaned.district),
            biz_classification_id=self._biz_id(
                db,
                cleaned.biz_mid_name,
                cleaned.biz_minor_name,
                cleaned.ksic_name,
            ),
            road_address=cleaned.road_address,
            parcel_address=cleaned.parcel_address,
            latitude=cleaned.latitude,
            longitude=cleaned.longitude,
            description=cleaned.description,
            image_url=cleaned.image_url,
        )
        if cleaned.avg_price is not None:
            entity.price = RestaurantPrice(avg_price=cleaned.avg_price)
        sig = (cleaned.signature_menu or "").strip()
        if sig:
            entity.menus = [RestaurantMenu(name=sig, is_signature=True, sort_order=0)]
        tag_links = self._tag_links(db, cleaned.ai_tags)
        if tag_links:
            entity.tag_links = tag_links
        return entity
