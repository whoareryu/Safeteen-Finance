from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy import text

from core.database import SyncSessionLocal

TITANIC_TABLE = "titanic_passengers"
logger = logging.getLogger(__name__)


@dataclass
class WalterPgRepositoryResult:
    items: list[dict[str, Any]]
    total: int
    page: int
    page_size: int


class WalterPgRepository:
    """Neon PostgreSQL에서 승객 명단 페이지를 읽는 아웃바운드 어댑터."""

    def get_passenger_page(self, *, page: int, page_size: int) -> WalterPgRepositoryResult:
        safe_page = max(1, page)
        safe_page_size = max(1, min(page_size, 500))
        offset = (safe_page - 1) * safe_page_size

        if SyncSessionLocal is None:
            raise RuntimeError("DB 세션이 초기화되지 않았습니다.")

        db = SyncSessionLocal()
        try:
            logger.info(
                "[Walter 경로] (4/4) Outbound adapter/outbound/pg/walter_pg_repository.py -> "
                "NeonDB table=%s page=%d page_size=%d offset=%d",
                TITANIC_TABLE,
                safe_page,
                safe_page_size,
                offset,
            )
            total_raw = db.execute(
                text(f"SELECT COUNT(*) FROM {TITANIC_TABLE}")
            ).scalar_one()
            total = int(total_raw or 0)

            rows = db.execute(
                text(
                    f"""
                    SELECT
                        passenger_id,
                        name,
                        gender,
                        pclass,
                        survived,
                        age
                    FROM {TITANIC_TABLE}
                    ORDER BY id
                    LIMIT :limit OFFSET :offset
                    """
                ),
                {"limit": safe_page_size, "offset": offset},
            ).mappings().all()

            return WalterPgRepositoryResult(
                items=[dict(r) for r in rows],
                total=total,
                page=safe_page,
                page_size=safe_page_size,
            )
        finally:
            db.close()

