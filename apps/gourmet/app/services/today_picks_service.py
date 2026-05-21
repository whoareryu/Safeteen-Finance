"""오늘의 맛집 — 카테고리별 2~3곳 (SgmaRestaurant ``restaurant`` 표준)."""

from __future__ import annotations

import datetime
import logging
import random
from collections import defaultdict

from sqlalchemy.orm import Session

from apps.gourmet.app.services.sgma_browse_service import (
    SgmaBrowseRow,
    bounded_sgma_slice,
    sgma_category_of,
)
from apps.gourmet.app.services.restaurant_location_service import distance_km_to_entity

logger = logging.getLogger(__name__)

CATEGORY_SLUGS: tuple[str, ...] = (
    "hansik",
    "ilsik",
    "jungsik",
    "yangsik",
    "asian",
    "bunsik",
    "cafe-dessert",
    "bar",
)

TODAY_SGMA_POOL = 36_000
PICKS_PER_CATEGORY_MIN = 2
PICKS_PER_CATEGORY_MAX = 3


def _pick_count_for_pool(pool_size: int) -> int:
    if pool_size >= PICKS_PER_CATEGORY_MAX:
        return PICKS_PER_CATEGORY_MAX
    if pool_size >= PICKS_PER_CATEGORY_MIN:
        return pool_size
    return pool_size


def get_today_picks(
    db: Session,
    today: datetime.date | None = None,
    *,
    user_lat: float | None = None,
    user_lng: float | None = None,
) -> tuple[datetime.date, list[SgmaBrowseRow]]:
    """카테고리별 2~3곳을 날짜 시드로 무작위 선택(일 단위 고정). DB ``daily_picks`` 미사용."""
    today = today or datetime.date.today()
    all_rows = bounded_sgma_slice(
        db,
        limit_rows=TODAY_SGMA_POOL,
        rotation_salt=0,
        day_ord=today.toordinal(),
    )
    if not all_rows:
        logger.warning("[gourmet] today-picks — 상가 데이터 없음")
        return today, []

    by_cat: dict[str, list[SgmaBrowseRow]] = defaultdict(list)
    for r in all_rows:
        by_cat[sgma_category_of(r)[0]].append(r)

    rng = random.Random(today.toordinal())
    picked: list[SgmaBrowseRow] = []
    for slug in CATEGORY_SLUGS:
        pool = by_cat.get(slug, [])
        if not pool:
            continue
        n = _pick_count_for_pool(len(pool))
        if n <= 0:
            continue
        shuffled = pool.copy()
        rng.shuffle(shuffled)
        chosen = shuffled[:n]
        picked.extend(chosen)

    if user_lat is not None and user_lng is not None and picked:
        picked = sorted(
            picked,
            key=lambda r: distance_km_to_entity(r, user_lat, user_lng),
        )

    logger.info("[gourmet] today-picks (sgma) — %s곳", len(picked))
    return today, picked


def expected_pick_count() -> int:
    """최대 카테고리 수 × 3."""
    return len(CATEGORY_SLUGS) * PICKS_PER_CATEGORY_MAX
