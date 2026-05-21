"""카테고리별 주제 행(넷플릭스 스타일) — SgmaRestaurant(``restaurant``) 배치."""

from __future__ import annotations

import logging
import zlib

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from apps.gourmet.app.data.category_topics import filter_topics_by_query, topics_for_category
from apps.gourmet.app.models.sgma_restaurant import SgmaRestaurant
from apps.gourmet.app.services.sgma_browse_service import (
    CATEGORY_LABEL_BY_SLUG,
    SgmaBrowseRow,
    bounded_sgma_slice,
    pick_sgmas,
    sgma_category_of,
    sgma_topic_row,
    trending_sgma_boost,
)

logger = logging.getLogger(__name__)

PICKS_PER_TOPIC_DEFAULT = 10


def _pool_for_category_slug(db: Session, category_slug: str) -> list[SgmaBrowseRow]:
    """전체 스캔 금지 — 여러 윈도우를 합쳐 해당 장르 풀 구성."""
    total = int(
        db.execute(select(func.count()).select_from(SgmaRestaurant)).scalar_one() or 0
    )
    salt = zlib.adler32(category_slug.encode("utf-8")) & 0xFFFFFFFF
    merged: dict[int, SgmaBrowseRow] = {}

    def take(rot: int, lim: int) -> None:
        for r in bounded_sgma_slice(
            db,
            limit_rows=lim,
            rotation_salt=rot,
            total_row_count=total,
        ):
            merged.setdefault(r.id, r)

    take(salt % 999_983, 16_000)
    take((salt ^ 0x9E3779B9) & 0xFFFFFFFF, 16_000)

    def filtered() -> list[SgmaBrowseRow]:
        return [r for r in merged.values() if sgma_category_of(r)[0] == category_slug]

    out = filtered()
    if len(out) < 30:
        take((salt + 13_311) & 0xFFFFFFFF, 28_000)
        out = filtered()

    if not out:
        for k in range(6):
            rows = bounded_sgma_slice(
                db,
                limit_rows=24_000,
                rotation_salt=(salt + k * 19_241) & 0xFFFFFFFF,
                total_row_count=total,
            )
            out = [r for r in rows if sgma_category_of(r)[0] == category_slug]
            if out:
                break
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
    """
    Returns (category_slug, category_label, rows, pagination_meta).
    Each row: topic fields + restaurants list.
    """
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
        logger.warning("[gourmet] browse — category=%s 상가 없음", category_slug)
        return category_slug, label, [], meta_dict()

    rows: list[dict] = []
    for topic in topic_slice:
        if topic.slug == "trending-now":
            picks = pick_sgmas(trending_sgma_boost(pool), topic.slug, limit=per_topic_limit)
        else:
            picks = pick_sgmas(pool, topic.slug, limit=per_topic_limit)
        rows.append(sgma_topic_row(topic, picks, user_lat=user_lat, user_lng=user_lng))

    return category_slug, label, rows, meta_dict()


def list_topic_catalog(category_slug: str) -> list[dict]:
    """검색 힌트용 전체 주제 목록 (식당 없이)."""
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
