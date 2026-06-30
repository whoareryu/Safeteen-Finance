"""브라우즈·카드 목록 순수 로직 — SQL·ORM 의존 없음."""

from __future__ import annotations

import hashlib
from collections import defaultdict

from restaurant.app.dtos.restaurant_browse_dto import RestaurantBrowseRow
from restaurant.data.category_topics import TopicDef
from restaurant.data.category_catalog import CATEGORY_LABEL_BY_SLUG
from restaurant.data.ingestion.category_normalizer import classify_sgma_category
from restaurant.data.restaurant_images import image_url_for_restaurant
from restaurant.domain.location import distance_km_to_entity


def browse_category_of(r: RestaurantBrowseRow) -> tuple[str, str]:
    slug = (r.category_slug or "").strip()
    label = (r.category_label or "").strip()
    if slug:
        return slug, label or CATEGORY_LABEL_BY_SLUG.get(slug, slug)
    slug, inferred = classify_sgma_category(
        r.biz_mid_name, r.biz_minor_name, r.ksic_name
    )
    return slug, label or CATEGORY_LABEL_BY_SLUG.get(slug, inferred)


def browse_display_name(r: RestaurantBrowseRow) -> str:
    nm = (r.name or "").strip()
    if nm:
        return nm
    s, b = (r.store_name or "").strip(), (r.branch_name or "").strip()
    if b:
        return f"{s} ({b})"
    return s or "상호 미상"


def score_row_for_topic(
    r: RestaurantBrowseRow, topic_slug: str, *, pick_salt: int = 0
) -> int:
    raw = f"{topic_slug}:{pick_salt}:{r.id}:{r.biz_number}:{r.name}"
    return int(hashlib.md5(raw.encode("utf-8")).hexdigest()[:8], 16)


def pick_rows(
    pool: list[RestaurantBrowseRow],
    topic_slug: str,
    *,
    limit: int,
    pick_salt: int = 0,
) -> list[RestaurantBrowseRow]:
    if not pool:
        return []
    ranked = sorted(pool, key=lambda r: score_row_for_topic(r, topic_slug, pick_salt=pick_salt))
    offset = score_row_for_topic(ranked[0], f"off-{topic_slug}", pick_salt=pick_salt) % max(
        len(ranked), 1
    )
    rotated = ranked[offset:] + ranked[:offset]
    return rotated[: min(limit, len(rotated))]


def trending_boost(pool: list[RestaurantBrowseRow]) -> list[RestaurantBrowseRow]:
    def key(r: RestaurantBrowseRow) -> tuple[int, int]:
        h = hash(r.biz_number or str(r.id)) % 8192
        return (-abs(h), r.id)

    return sorted(pool, key=key)


def pick_mixed_by_category(
    pool: list[RestaurantBrowseRow],
    topic_slug: str,
    *,
    limit: int,
    pick_salt: int = 0,
) -> list[RestaurantBrowseRow]:
    if not pool:
        return []

    by_cat: dict[str, list[RestaurantBrowseRow]] = defaultdict(list)
    for r in pool:
        by_cat[browse_category_of(r)[0]].append(r)

    ranked: dict[str, list[RestaurantBrowseRow]] = {
        cat: sorted(rs, key=lambda r: score_row_for_topic(r, topic_slug, pick_salt=pick_salt))
        for cat, rs in by_cat.items()
    }
    indices = {cat: 0 for cat in ranked}
    cats = list(ranked.keys())
    out: list[RestaurantBrowseRow] = []
    seen_ids: set[int] = set()

    while len(out) < limit and cats:
        progressed = False
        for cat in cats:
            lst = ranked[cat]
            idx = indices[cat]
            while idx < len(lst):
                r = lst[idx]
                indices[cat] = idx + 1
                idx += 1
                if r.id not in seen_ids:
                    out.append(r)
                    seen_ids.add(r.id)
                    progressed = True
                    break
            if len(out) >= limit:
                break
        if not progressed:
            break

    return out


def sort_rows_by_distance(
    rows: list[RestaurantBrowseRow],
    user_lat: float,
    user_lng: float,
) -> list[RestaurantBrowseRow]:
    return sorted(
        rows,
        key=lambda r: distance_km_to_entity(r, user_lat, user_lng),
    )


def rows_to_card_summaries(
    rows: list[RestaurantBrowseRow],
    *,
    user_lat: float | None = None,
    user_lng: float | None = None,
    with_rank: bool = False,
    with_category: bool = False,
) -> list[dict]:
    ordered = rows
    if user_lat is not None and user_lng is not None:
        ordered = sort_rows_by_distance(rows, user_lat, user_lng)

    items: list[dict] = []
    for i, r in enumerate(ordered, start=1):
        slug, label = browse_category_of(r)
        nm = browse_display_name(r)
        img = (r.image_url or "").strip() or image_url_for_restaurant(nm, slug, "")
        item: dict = {
            "id": r.id,
            "name": nm,
            "image_url": img,
            "district": r.district or r.sigungu_name or "",
        }
        if with_rank:
            item["rank"] = i
        if with_category:
            item["category_slug"] = slug
            item["category_label"] = label
        if user_lat is not None and user_lng is not None:
            item["distance_km"] = round(
                distance_km_to_entity(r, user_lat, user_lng), 1
            )
        items.append(item)
    return items


def browse_topic_row(
    topic: TopicDef,
    picks: list[RestaurantBrowseRow],
    *,
    user_lat: float | None = None,
    user_lng: float | None = None,
    link_title: bool = True,
    with_category_on_cards: bool = False,
) -> dict:
    return {
        "slug": topic.slug,
        "title": topic.title,
        "subtitle": topic.subtitle,
        "emoji": topic.emoji,
        "keywords": list(topic.keywords),
        "restaurants": rows_to_card_summaries(
            picks,
            user_lat=user_lat,
            user_lng=user_lng,
            with_category=with_category_on_cards,
        ),
        "link_title": link_title,
    }
