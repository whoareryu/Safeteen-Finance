"""공공 CSV → ``restaurants`` 테이블 배치 적재."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from apps.gourmet.app.data.ingestion.restaurant_row_cleaner import RestaurantCsvRowCleaner
from apps.gourmet.app.models.restaurant import Restaurant
from apps.gourmet.app.repositories.restaurant_repository import RestaurantRepository

logger = logging.getLogger(__name__)


class CsvRestaurantImporter:
    """정제 모듈 + Repository bulk insert 조합."""

    def __init__(
        self,
        *,
        cleaner: RestaurantCsvRowCleaner | None = None,
        repository: RestaurantRepository | None = None,
        chunk_size: int = 1000,
    ) -> None:
        self._cleaner = cleaner or RestaurantCsvRowCleaner()
        self._repo = repository or RestaurantRepository()
        self._chunk_size = chunk_size

    def import_file(
        self,
        db: Session,
        csv_path: Path,
        *,
        replace_all: bool = True,
    ) -> tuple[int, int]:
        """CSV 전건 적재. ``replace_all`` 이면 기존 ``restaurants`` 비운 뒤 삽입."""
        if not csv_path.is_file():
            raise FileNotFoundError(str(csv_path))

        deleted = 0
        if replace_all:
            deleted = self._repo.delete_all(db)

        seen_biz: set[str] = set()
        pending: list[Restaurant] = []
        inserted = 0
        skipped = 0

        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for raw in reader:
                if (raw.get("상가업소번호") or "").strip() in seen_biz:
                    skipped += 1
                    continue

                cleaned = self._cleaner.clean(raw)
                if cleaned is None:
                    skipped += 1
                    continue

                seen_biz.add(cleaned.biz_number)
                pending.append(self._to_entity(cleaned))
                if len(pending) >= self._chunk_size:
                    inserted += self._repo.bulk_insert(db, pending, commit=True)
                    pending.clear()

        if pending:
            inserted += self._repo.bulk_insert(db, pending, commit=True)

        logger.info(
            "[gourmet import] path=%s inserted=%s deleted=%s skipped_dup_or_invalid=%s",
            csv_path,
            inserted,
            deleted,
            skipped,
        )
        return inserted, deleted

    @staticmethod
    def _to_entity(row) -> Restaurant:
        return Restaurant(
            biz_number=row.biz_number,
            name=row.name,
            store_name=row.store_name,
            branch_name=row.branch_name,
            category_slug=row.category_slug,
            category_label=row.category_label,
            district=row.district,
            sigungu_name=row.sigungu_name,
            road_address=row.road_address,
            parcel_address=row.parcel_address,
            latitude=row.latitude,
            longitude=row.longitude,
            avg_price=row.avg_price,
            signature_menu=row.signature_menu,
            ai_tags=row.ai_tags,
            description=row.description,
            image_url=row.image_url,
            biz_mid_name=row.biz_mid_name,
            biz_minor_name=row.biz_minor_name,
            ksic_name=row.ksic_name,
        )
