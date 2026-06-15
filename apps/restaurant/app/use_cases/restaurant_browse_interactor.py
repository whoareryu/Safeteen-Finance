"""``restaurants`` 테이블 기반 브라우즈·카드 목록 헬퍼."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from restaurant.data.category_topics import TopicDef
from restaurant.data.category_catalog import CATEGORY_LABEL_BY_SLUG
from restaurant.data.ingestion.category_normalizer import classify_sgma_category
from restaurant.data.restaurant_images import image_url_for_restaurant
from restaurant.adapter.outbound.orm.biz_classification_orm import BizClassification
from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.orm.sigungu_district_orm import SigunguDistrict
from restaurant.app.use_cases.restaurant_location_interactor import distance_km_to_entity
from restaurant.app.ports.input.restaurant_browse_use_case import RestaurantBrowseUseCase
from restaurant.adapter.inbound.api.schemas.restaurant_browse_schema import RestaurantBrowseSchema
from restaurant.app.dtos.restaurant_browse_dto import RestaurantBrowseQuery, RestaurantBrowseResponse
from restaurant.app.ports.output.restaurant_browse_repository import RestaurantBrowseRepository


@dataclass(slots=True)
class RestaurantBrowseRow:
    """목록·검색 풀용 — 필요 컬럼만 projection."""

    id: int
    name: str
    store_name: str
    branch_name: str
    category_slug: str
    category_label: str
    biz_mid_name: str
    biz_minor_name: str
    ksic_name: str
    biz_number: str
    district: str
    sigungu_name: str
    latitude: float | None
    longitude: float | None
    road_address: str = ""
    parcel_address: str = ""
    image_url: str = ""


RESTAURANT_BROWSE_COLUMNS = (
    Restaurant.id,
    Restaurant.name,
    Restaurant.store_name,
    Restaurant.branch_name,
    FoodCategory.slug,
    FoodCategory.label,
    BizClassification.biz_mid_name,
    BizClassification.biz_minor_name,
    BizClassification.ksic_name,
    Restaurant.biz_number,
    SigunguDistrict.district_label,
    SigunguDistrict.sigungu_name,
    Restaurant.latitude,
    Restaurant.longitude,
    Restaurant.road_address,
    Restaurant.parcel_address,
    Restaurant.image_url,
)


def _browse_row_from_tuple(t: tuple) -> RestaurantBrowseRow:
    return RestaurantBrowseRow(
        id=int(t[0]),
        name=str(t[1] or ""),
        store_name=str(t[2] or ""),
        branch_name=str(t[3] or ""),
        category_slug=str(t[4] or "hansik"),
        category_label=str(t[5] or ""),
        biz_mid_name=str(t[6] or ""),
        biz_minor_name=str(t[7] or ""),
        ksic_name=str(t[8] or ""),
        biz_number=str(t[9] or ""),
        district=str(t[10] or ""),
        sigungu_name=str(t[11] or ""),
        latitude=t[12],
        longitude=t[13],
        road_address=str(t[14] or ""),
        parcel_address=str(t[15] or ""),
        image_url=str(t[16] or ""),
    )


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


def _browse_base_select():
    return (
        select(*RESTAURANT_BROWSE_COLUMNS)
        .join(FoodCategory, Restaurant.category_id == FoodCategory.id)
        .join(SigunguDistrict, Restaurant.sigungu_id == SigunguDistrict.id)
        .join(
            BizClassification,
            Restaurant.biz_classification_id == BizClassification.id,
        )
    )


def count_restaurants(db: Session, *, category_slug: str | None = None) -> int:
    stmt = select(func.count()).select_from(Restaurant).join(
        FoodCategory, Restaurant.category_id == FoodCategory.id
    )
    if category_slug:
        stmt = stmt.where(FoodCategory.slug == category_slug)
    return int(db.execute(stmt).scalar_one() or 0)


def bounded_restaurant_slice(
    db: Session,
    *,
    limit_rows: int = 10_000,
    rotation_salt: int = 0,
    day_ord: int | None = None,
    total_row_count: int | None = None,
    category_slug: str | None = None,
) -> list[RestaurantBrowseRow]:
    """대량 ``restaurants`` — id 순 윈도우(선택: 카테고리 필터)."""
    do = day_ord if day_ord is not None else date.today().toordinal()
    if total_row_count is not None:
        cnt = int(total_row_count)
    else:
        cnt = count_restaurants(db, category_slug=category_slug)
    if cnt == 0:
        return []
    n = min(limit_rows, cnt)
    span = cnt - n
    off = ((do * 79_691 + rotation_salt * 3_961) % (span + 1)) if span > 0 else 0
    stmt = _browse_base_select()
    if category_slug:
        stmt = stmt.where(FoodCategory.slug == category_slug)
    stmt = stmt.order_by(Restaurant.id).offset(off).limit(n)
    return [_browse_row_from_tuple(t) for t in db.execute(stmt).all()]


RESTAURANT_TEXT_SEARCH_COLUMNS = (
    Restaurant.name,
    Restaurant.store_name,
    Restaurant.branch_name,
    BizClassification.biz_mid_name,
    BizClassification.biz_minor_name,
    BizClassification.ksic_name,
    SigunguDistrict.district_label,
    SigunguDistrict.sigungu_name,
    Restaurant.road_address,
    Restaurant.parcel_address,
)


def fetch_text_search_candidates(
    db: Session,
    *,
    patterns: list[str],
    limit: int = 1_600,
) -> list[RestaurantBrowseRow]:
    uniq: list[str] = []
    for p in patterns:
        if p and p not in uniq:
            uniq.append(p)
        if len(uniq) >= 14:
            break
    if not uniq:
        return bounded_restaurant_slice(db, limit_rows=min(6_000, limit * 4))
    parts = [or_(*[col.ilike(p) for col in RESTAURANT_TEXT_SEARCH_COLUMNS]) for p in uniq]
    cond = or_(*parts) if len(parts) > 1 else parts[0]
    stmt = _browse_base_select().where(cond).limit(limit)
    rows = [_browse_row_from_tuple(t) for t in db.execute(stmt).all()]
    if not rows:
        return bounded_restaurant_slice(db, limit_rows=min(8_000, limit * 5))
    return rows


def restaurant_display_name(db: Session, store_id: int) -> str | None:
    r = db.get(Restaurant, store_id)
    if r is None:
        return None
    return r.display_name()


class RestaurantBrowseInteractor(RestaurantBrowseUseCase):
    def __init__(self, repository: RestaurantBrowseRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: RestaurantBrowseSchema) -> RestaurantBrowseResponse:
        return await self.repository.introduce_myself(
            RestaurantBrowseQuery(id=schema.id, name=schema.name)
        )
