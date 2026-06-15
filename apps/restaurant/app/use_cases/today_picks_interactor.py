"""오늘의 맛집 — 카테고리별 2~3곳 (``restaurants``)."""

from __future__ import annotations

import datetime
import logging
import random
from collections import defaultdict

from sqlalchemy.orm import Session

from restaurant.app.use_cases.restaurant_browse_interactor import (
    RestaurantBrowseRow,
    bounded_restaurant_slice,
    browse_category_of,
)
from restaurant.app.use_cases.restaurant_location_interactor import distance_km_to_entity
from restaurant.app.ports.input.today_picks_use_case import TodayPicksUseCase
from restaurant.adapter.inbound.api.schemas.today_picks_schema import TodayPicksSchema
from restaurant.app.dtos.today_picks_dto import TodayPicksQuery, TodayPicksResponse
from restaurant.app.ports.output.today_picks_repository import TodayPicksRepository


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

TODAY_BROWSE_POOL = 36_000
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
) -> tuple[datetime.date, list[RestaurantBrowseRow]]:
    today = today or datetime.date.today()
    all_rows = bounded_restaurant_slice(
        db,
        limit_rows=TODAY_BROWSE_POOL,
        rotation_salt=0,
        day_ord=today.toordinal(),
    )
    if not all_rows:
        logger.warning("[gourmet] today-picks — 매장 데이터 없음")
        return today, []

    by_cat: dict[str, list[RestaurantBrowseRow]] = defaultdict(list)
    for r in all_rows:
        by_cat[browse_category_of(r)[0]].append(r)

    rng = random.Random(today.toordinal())
    picked: list[RestaurantBrowseRow] = []
    for slug in CATEGORY_SLUGS:
        pool = by_cat.get(slug, [])
        if not pool:
            continue
        n = _pick_count_for_pool(len(pool))
        if n <= 0:
            continue
        shuffled = pool.copy()
        rng.shuffle(shuffled)
        picked.extend(shuffled[:n])

    if user_lat is not None and user_lng is not None and picked:
        picked = sorted(
            picked,
            key=lambda r: distance_km_to_entity(r, user_lat, user_lng),
        )

    logger.info("[gourmet] today-picks — %s곳", len(picked))
    return today, picked


def expected_pick_count() -> int:
    return len(CATEGORY_SLUGS) * PICKS_PER_CATEGORY_MAX


class TodayPicksInteractor(TodayPicksUseCase):
    def __init__(self, repository: TodayPicksRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: TodayPicksSchema) -> TodayPicksResponse:
        return await self.repository.introduce_myself(
            TodayPicksQuery(id=schema.id, name=schema.name)
        )
