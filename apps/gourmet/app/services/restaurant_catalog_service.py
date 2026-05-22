"""``restaurants`` CSV 적재 — 서버 기동 시 선택적 1회."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.gourmet.app.models.restaurant import Restaurant
from apps.gourmet.app.services.restaurant_domain_service import RestaurantDomainService

logger = logging.getLogger(__name__)

_DEFAULT_CSV = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "소상공인시장진흥공단_음식분류정보_서울_202603.csv"
)


def maybe_import_restaurants_on_startup(db: Session) -> None:
    """
    환경변수 ``RESTAURANTS_CSV`` 또는 ``SGMA_RESTAURANT_CSV`` 경로가 있고
    ``restaurants`` 가 비어 있으면 CSV를 적재합니다.
    """
    raw = (
        os.getenv("RESTAURANTS_CSV", "").strip()
        or os.getenv("SGMA_RESTAURANT_CSV", "").strip()
    )
    if not raw:
        return

    existing = int(
        db.execute(select(func.count()).select_from(Restaurant)).scalar_one() or 0
    )
    if existing > 0:
        logger.info(
            "[gourmet] restaurants 이미 %s건 — 시작 시 CSV 적재 생략", existing
        )
        return

    path = Path(raw).expanduser()
    if not path.is_file() and _DEFAULT_CSV.is_file():
        path = _DEFAULT_CSV

    try:
        inserted, deleted = RestaurantDomainService().import_from_csv(
            db, path, replace_all=True
        )
        logger.info(
            "[gourmet] restaurants 시작 적재 — 삭제(대략)=%s 삽입=%s 경로=%s",
            deleted,
            inserted,
            path,
        )
    except FileNotFoundError:
        logger.warning("[gourmet] RESTAURANTS_CSV 파일 없음: %s", path)
    except Exception:
        logger.exception("[gourmet] restaurants CSV 적재 실패 — path=%s", path)
        db.rollback()
