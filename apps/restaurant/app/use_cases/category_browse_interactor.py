"""카테고리별 주제 행(넷플릭스 스타일) — ``restaurants`` 배치."""

from __future__ import annotations

import logging
import zlib

from sqlalchemy.orm import Session

from restaurant.data.category_topics import filter_topics_by_query, topics_for_category
from restaurant.app.use_cases.restaurant_browse_interactor import (
from restaurant.app.ports.input.category_browse_use_case import CategoryBrowseUseCase
from restaurant.adapter.inbound.api.schemas.category_browse_schema import CategoryBrowseSchema
from restaurant.app.dtos.category_browse_dto import CategoryBrowseQuery, CategoryBrowseResponse
from restaurant.app.ports.output.category_browse_repository import CategoryBrowseRepository

    CATEGORY_LABEL_BY_SLUG,
    RestaurantBrowseRow,
    bounded_restaurant_slice,
    browse_topic_row,
    pick_rows,
    trending_boost,
)

logger = logging.getLogger(__name__)

PICKS_PER_TOPIC_DEFAULT = 10


def _pool_for_category_slug(db: Session, category_slug: str) -> list[RestaurantBrowseRow]:
    """해당 장르 윈도우 2~3개를 합쳐 후보 풀 구성."""
    from restaurant.app.use_cases.restaurant_browse_interactor import count_restaurants

    total = count_restaurants(db, category_slug=category_slug)
    if total == 0:
        return []

    salt = zlib.adler32(category_slug.encode("utf-8")) & 0xFFFFFFFF
    merged: dict[int, RestaurantBrowseRow] = {}

    def take(rot: int, lim: int) -> None:
        for r in bounded_restaurant_slice(
            db,
            limit_rows=lim,
            rotation_salt=rot,
            total_row_count=total,
            category_slug=category_slug,
        ):
            merged.setdefault(r.id, r)

    take(salt % 999_983, min(16_000, total))
    take((salt ^ 0x9E3779B9) & 0xFFFFFFFF, min(16_000, total))

    out = list(merged.values())
    if len(out) < 30:
        take((salt + 13_311) & 0xFFFFFFFF, min(28_000, total))
        out = list(merged.values())
    return out


def get_category_browse(
    db: Session,
    category_slug: str,
    *,
    q: str | None = None,
    user_lat: float | None = None,
    user_lng: float | None = None,
    topic_offset: int = 0,
    topic_limit: int = 4,
    per_topic_limit: int = PICKS_PER_TOPIC_DEFAULT,
) -> tuple[str, str, list[dict], dict]:
    label = CATEGORY_LABEL_BY_SLUG.get(category_slug, category_slug)
    topics = topics_for_category(category_slug)
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

    pool = _pool_for_category_slug(db, category_slug)
    if not pool:
        logger.warning("[gourmet] browse — category=%s 매장 없음", category_slug)
        return category_slug, label, [], meta_dict()

    rows: list[dict] = []
    for topic in topic_slice:
        if topic.slug == "trending-now":
            picks = pick_rows(trending_boost(pool), topic.slug, limit=per_topic_limit)
        else:
            picks = pick_rows(pool, topic.slug, limit=per_topic_limit)
        rows.append(browse_topic_row(topic, picks, user_lat=user_lat, user_lng=user_lng))

    return category_slug, label, rows, meta_dict()


def list_topic_catalog(category_slug: str) -> list[dict]:
    return [
        {
            "slug": t.slug,
            "title": t.title,
            "subtitle": t.subtitle,
            "emoji": t.emoji,
            "keywords": list(t.keywords),
        }
        for t in topics_for_category(category_slug)
    ]


class CategoryBrowseInteractor(CategoryBrowseUseCase):
    def __init__(self, repository: CategoryBrowseRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: CategoryBrowseSchema) -> CategoryBrowseResponse:
        return await self.repository.introduce_myself(
            CategoryBrowseQuery(id=schema.id, name=schema.name)
        )
