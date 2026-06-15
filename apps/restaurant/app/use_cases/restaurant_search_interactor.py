"""검색어 기반 맛집 추천 — ``restaurants`` ILIKE·윈도우 기반."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from restaurant.data.category_topics import (
    CATEGORY_EXTRA_TOPICS,
    COMMON_TOPICS,
    TopicDef,
    filter_topics_by_query,
)
from restaurant.data.search_keywords import (
    expand_search_terms,
    topic_slugs_for_query,
)
from restaurant.app.use_cases.restaurant_browse_interactor import (
    RestaurantBrowseRow,
    bounded_restaurant_slice,
    browse_category_of,
    fetch_text_search_candidates,
    pick_mixed_by_category,
    rows_to_card_summaries,
    sort_rows_by_distance,
)
from restaurant.app.use_cases.restaurant_location_interactor import distance_km_to_entity
from restaurant.app.ports.input.restaurant_search_use_case import RestaurantSearchUseCase
from restaurant.adapter.inbound.api.schemas.restaurant_search_schema import RestaurantSearchSchema
from restaurant.app.dtos.restaurant_search_dto import RestaurantSearchQuery, RestaurantSearchResponse
from restaurant.app.ports.output.restaurant_search_repository import RestaurantSearchRepository


logger = logging.getLogger(__name__)

INTERNAL_SEARCH_RESULTS_CAP = 200
DEFAULT_SEARCH_PAGE_SIZE = 10


def _all_topics() -> list[TopicDef]:
    topics = list(COMMON_TOPICS)
    for extras in CATEGORY_EXTRA_TOPICS.values():
        topics.extend(extras)
    return topics


def _haystack(r: RestaurantBrowseRow) -> str:
    parts = [
        r.name,
        r.store_name,
        r.branch_name,
        r.biz_minor_name,
        r.biz_mid_name,
        r.ksic_name,
        r.district,
        r.sigungu_name,
        r.road_address,
        r.parcel_address,
        r.category_label,
    ]
    return " ".join(p for p in parts if p).lower()


def _topic_applies(topic: TopicDef, r: RestaurantBrowseRow) -> bool:
    if topic.category_slugs and browse_category_of(r)[0] not in topic.category_slugs:
        return False
    return True


def _score_row(
    r: RestaurantBrowseRow,
    terms: list[str],
    *,
    primary: str,
    boosted_slugs: set[str],
) -> int:
    hay = _haystack(r)
    score = 0
    for term in terms:
        if term in hay:
            score += 20 if term == primary else 6
    topics_by_slug = {t.slug: t for t in _all_topics()}
    for slug in boosted_slugs:
        topic = topics_by_slug.get(slug)
        if topic and _topic_applies(topic, r):
            score += 12
    score += hash(r.biz_number or str(r.id)) % 10
    return score


def _build_summary(
    q: str,
    terms: list[str],
    topics: list[TopicDef],
    count: int,
    *,
    nearby: bool = False,
) -> str:
    prefix = "내 주변 " if nearby else ""
    if topics:
        titles = " · ".join(f"{t.emoji} {t.title}" for t in topics[:2])
        return f'"{q}" — {prefix}{titles} 등 {count}곳'
    if "여름" in terms or "여름" in q:
        return f'"{q}" — {prefix}여름·시원한 메뉴 맛집 {count}곳'
    if "해장" in terms or "해장" in q:
        return f'"{q}" — {prefix}해장·국물 맛집 {count}곳'
    return f'"{q}" {prefix}검색 결과 {count}곳'


def search_restaurants(
    db: Session,
    q: str,
    *,
    user_lat: float | None = None,
    user_lng: float | None = None,
    offset: int = 0,
    limit: int = DEFAULT_SEARCH_PAGE_SIZE,
) -> dict:
    raw = q.strip()
    if not raw:
        return {
            "query": "",
            "summary": "",
            "matched_topics": [],
            "restaurants": [],
            "pagination": {
                "offset": 0,
                "limit": max(1, limit),
                "total": 0,
                "has_more": False,
            },
        }

    terms = expand_search_terms(raw)

    patterns: list[str] = []
    t0 = raw.strip()
    if t0:
        patterns.append(f"%{t0}%")
    for term in terms:
        u = term.strip()
        if len(u) >= 2:
            p = f"%{u}%"
            if p not in patterns:
                patterns.append(p)

    rows_from_fts = fetch_text_search_candidates(
        db, patterns=patterns, limit=2_200
    )
    by_id = {r.id: r for r in rows_from_fts}
    if len(by_id) < 800:
        for r in bounded_restaurant_slice(
            db,
            limit_rows=14_000,
            rotation_salt=abs(hash(raw)) % (2**31 - 1),
        ):
            by_id.setdefault(r.id, r)
    all_rows = list(by_id.values())

    if not all_rows:
        return {
            "query": raw,
            "summary": f'"{raw}" — 데이터 없음',
            "matched_topics": [],
            "restaurants": [],
            "nearby_mode": user_lat is not None and user_lng is not None,
            "pagination": {
                "offset": offset,
                "limit": limit,
                "total": 0,
                "has_more": False,
            },
        }

    primary = raw.lower()
    boosted_slugs = set(topic_slugs_for_query(raw, terms))
    matched_topics = filter_topics_by_query(_all_topics(), raw)
    for t in matched_topics:
        boosted_slugs.add(t.slug)

    scored: list[tuple[RestaurantBrowseRow, int]] = []
    for r in all_rows:
        s = _score_row(r, terms, primary=primary, boosted_slugs=boosted_slugs)
        if s > 0:
            scored.append((r, s))

    picked: list[RestaurantBrowseRow] = []
    seen: set[int] = set()

    if scored:
        if user_lat is not None and user_lng is not None:
            scored.sort(
                key=lambda x: (
                    -x[1],
                    distance_km_to_entity(x[0], user_lat, user_lng),
                )
            )
        else:
            scored.sort(key=lambda x: (-x[1], x[0].id))
        for r, _ in scored:
            if r.id in seen:
                continue
            seen.add(r.id)
            picked.append(r)
            if len(picked) >= INTERNAL_SEARCH_RESULTS_CAP:
                break

    if len(picked) < INTERNAL_SEARCH_RESULTS_CAP and matched_topics:
        for topic in matched_topics[:4]:
            pool = [r for r in all_rows if _topic_applies(topic, r) and r.id not in seen]
            if not pool:
                pool = [r for r in all_rows if r.id not in seen]
            extra = pick_mixed_by_category(pool, topic.slug, limit=8)
            for r in extra:
                if r.id in seen:
                    continue
                seen.add(r.id)
                picked.append(r)
                if len(picked) >= INTERNAL_SEARCH_RESULTS_CAP:
                    break
            if len(picked) >= INTERNAL_SEARCH_RESULTS_CAP:
                break

    if user_lat is not None and user_lng is not None and picked:
        picked = sort_rows_by_distance(picked, user_lat, user_lng)

    items = rows_to_card_summaries(
        picked,
        user_lat=user_lat,
        user_lng=user_lng,
        with_category=True,
    )
    total_matched = len(items)
    slice_end = offset + limit
    page_items = items[offset:slice_end]

    summary = _build_summary(
        raw, terms, matched_topics, total_matched, nearby=user_lat is not None
    )
    logger.info("[gourmet] search q=%s — %s건", raw, total_matched)

    return {
        "query": raw,
        "summary": summary,
        "nearby_mode": user_lat is not None and user_lng is not None,
        "matched_topics": [
            {"slug": t.slug, "title": t.title, "emoji": t.emoji}
            for t in matched_topics[:6]
        ],
        "restaurants": page_items,
        "pagination": {
            "offset": offset,
            "limit": limit,
            "total": total_matched,
            "has_more": slice_end < total_matched,
        },
    }


class RestaurantSearchInteractor(RestaurantSearchUseCase):
    def __init__(self, repository: RestaurantSearchRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: RestaurantSearchSchema) -> RestaurantSearchResponse:
        return await self.repository.introduce_myself(
            RestaurantSearchQuery(id=schema.id, name=schema.name)
        )
