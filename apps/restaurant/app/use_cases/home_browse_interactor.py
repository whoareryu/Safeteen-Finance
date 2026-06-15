"""메인 홈 — 주제당 ``restaurants`` 를 한 행에 섞어서 반환."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session

from restaurant.data.category_topics import home_feed_topics
from restaurant.app.use_cases.restaurant_browse_interactor import (
from restaurant.app.ports.input.home_browse_use_case import HomeBrowseUseCase
from restaurant.adapter.inbound.api.schemas.home_browse_schema import HomeBrowseSchema
from restaurant.app.dtos.home_browse_dto import HomeBrowseQuery, HomeBrowseResponse
from restaurant.app.ports.output.home_browse_repository import HomeBrowseRepository

    RestaurantBrowseRow,
    bounded_restaurant_slice,
    browse_topic_row,
    pick_mixed_by_category,
    pick_rows,
    sort_rows_by_distance,
    trending_boost,
)

HOME_BROWSE_POOL = 12_000

logger = logging.getLogger(__name__)

HOME_PICKS_PER_TOPIC = 10
MAX_TOPICS_PER_RESTAURANT = 2


def _eligible_for_topic(
    pool: list[RestaurantBrowseRow],
    usage_count: dict[int, int],
) -> list[RestaurantBrowseRow]:
    return [
        r
        for r in pool
        if usage_count.get(r.id, 0) < MAX_TOPICS_PER_RESTAURANT
    ]


def get_home_browse(
    db: Session,
    *,
    q: str | None = None,
    user_lat: float | None = None,
    user_lng: float | None = None,
    topic_offset: int = 0,
    topic_limit: int = 4,
    per_topic_limit: int = HOME_PICKS_PER_TOPIC,
) -> tuple[list[dict], dict]:
    topics = home_feed_topics(q)
    total_topics_filtered = len(topics)
    end_ix = topic_offset + topic_limit
    topic_slice = topics[topic_offset:end_ix]

    def meta_dict() -> dict:
        return {
            "topic_offset": topic_offset,
            "topic_limit": topic_limit,
            "per_topic_limit": per_topic_limit,
            "total_topics": total_topics_filtered,
            "has_more": end_ix < total_topics_filtered,
        }

    # 스크롤 페이지마다 다른 DB 윈도우 + 다른 pick 시드 → 매장·구성 다양화
    pool_salt = topic_offset * 79_691 + date.today().toordinal()
    all_rows = bounded_restaurant_slice(
        db,
        limit_rows=HOME_BROWSE_POOL,
        rotation_salt=pool_salt,
        day_ord=date.today().toordinal(),
    )
    if not all_rows:
        return [], meta_dict()

    rows: list[dict] = []
    topic_usage_count: dict[int, int] = defaultdict(int)
    pick_salt = topic_offset

    for topic in topic_slice:
        eligible = _eligible_for_topic(all_rows, topic_usage_count)
        if not eligible:
            continue

        if topic.slug == "trending-now":
            pool = trending_boost(eligible)
            picks = pick_rows(
                pool, topic.slug, limit=per_topic_limit, pick_salt=pick_salt
            )
        else:
            picks = pick_mixed_by_category(
                eligible,
                topic.slug,
                limit=per_topic_limit,
                pick_salt=pick_salt,
            )
        if not picks:
            continue

        if user_lat is not None and user_lng is not None:
            picks = sort_rows_by_distance(picks, user_lat, user_lng)

        for r in picks:
            topic_usage_count[r.id] += 1

        rows.append(
            browse_topic_row(
                topic,
                picks,
                user_lat=user_lat,
                user_lng=user_lng,
                link_title=True,
                with_category_on_cards=True,
            )
        )

    logger.info(
        "[gourmet] home-browse — %s/%s 주제 행 (offset=%s total_topics=%s nearby=%s)",
        len(rows),
        len(topic_slice),
        topic_offset,
        total_topics_filtered,
        user_lat is not None,
    )
    return rows, meta_dict()


class HomeBrowseInteractor(HomeBrowseUseCase):
    def __init__(self, repository: HomeBrowseRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: HomeBrowseSchema) -> HomeBrowseResponse:
        return await self.repository.introduce_myself(
            HomeBrowseQuery(id=schema.id, name=schema.name)
        )
