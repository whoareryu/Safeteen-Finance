"""메인 홈 — 주제당 SgmaRestaurant(``restaurant``)를 한 행에 섞어서 반환."""

from __future__ import annotations

import logging
from collections import defaultdict

from sqlalchemy.orm import Session

from apps.gourmet.app.data.category_topics import COMMON_TOPICS, filter_topics_by_query
from apps.gourmet.app.services.sgma_browse_service import (
    SgmaBrowseRow,
    bounded_sgma_slice,
    pick_mixed_sgma_by_category,
    pick_sgmas,
    sgma_topic_row,
    sort_sgmas_by_distance,
    trending_sgma_boost,
)

# Neon 타임아웃 방지 — 매 요청 ~14만 행 적재 금지
HOME_SGMA_POOL = 12_000

logger = logging.getLogger(__name__)

HOME_PICKS_PER_TOPIC = 10
MAX_HOME_TOPICS = 16
MAX_TOPICS_PER_RESTAURANT = 2


def _eligible_for_topic(
    pool: list[SgmaBrowseRow],
    usage_count: dict[int, int],
) -> list[SgmaBrowseRow]:
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
    topics = list(COMMON_TOPICS[:MAX_HOME_TOPICS])
    if q:
        topics = filter_topics_by_query(topics, q)

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

    all_rows = bounded_sgma_slice(db, limit_rows=HOME_SGMA_POOL, rotation_salt=0)
    if not all_rows:
        return [], meta_dict()

    rows: list[dict] = []
    topic_usage_count: dict[int, int] = defaultdict(int)

    for topic in topic_slice:
        eligible = _eligible_for_topic(all_rows, topic_usage_count)
        if not eligible:
            continue

        if topic.slug == "trending-now":
            pool = trending_sgma_boost(eligible)
            picks = pick_sgmas(pool, topic.slug, limit=per_topic_limit)
        else:
            picks = pick_mixed_sgma_by_category(
                eligible, topic.slug, limit=per_topic_limit
            )
        if not picks:
            continue

        if user_lat is not None and user_lng is not None:
            picks = sort_sgmas_by_distance(picks, user_lat, user_lng)

        for r in picks:
            topic_usage_count[r.id] += 1

        rows.append(
            sgma_topic_row(
                topic,
                picks,
                user_lat=user_lat,
                user_lng=user_lng,
                link_title=True,
                with_category_on_cards=True,
            )
        )

    logger.info(
        "[gourmet] home-browse (sgma) — %s개 주제 행 (식당당 최대 %s주제, nearby=%s)",
        len(rows),
        MAX_TOPICS_PER_RESTAURANT,
        user_lat is not None,
    )
    return rows, meta_dict()
