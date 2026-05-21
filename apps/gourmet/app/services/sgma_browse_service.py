"""SgmaRestaurant(테이블 ``restaurant``) 기반 브라우즈·카드 목록 헬퍼."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from apps.gourmet.app.data.category_topics import TopicDef
from apps.gourmet.app.data.restaurant_images import image_url_for_restaurant
from apps.gourmet.app.models.sgma_restaurant import SgmaRestaurant
from apps.gourmet.app.services.restaurant_location_service import distance_km_to_entity
from apps.gourmet.app.services.sgma_restaurant_service import classify_sgma_category

CATEGORY_LABEL_BY_SLUG: dict[str, str] = {
    "hansik": "한식",
    "ilsik": "일식",
    "jungsik": "중식",
    "yangsik": "양식",
    "asian": "아시안",
    "bunsik": "분식",
    "cafe-dessert": "카페·디저트",
    "bar": "바",
}


@dataclass(slots=True)
class SgmaBrowseRow:
    """목록·검색 풀용 — ORM 전체 행 대신 필요 컬럼만."""

    id: int
    store_name: str
    branch_name: str
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


SGMA_BROWSE_COLUMNS = (
    SgmaRestaurant.id,
    SgmaRestaurant.store_name,
    SgmaRestaurant.branch_name,
    SgmaRestaurant.biz_mid_name,
    SgmaRestaurant.biz_minor_name,
    SgmaRestaurant.ksic_name,
    SgmaRestaurant.biz_number,
    SgmaRestaurant.district,
    SgmaRestaurant.sigungu_name,
    SgmaRestaurant.latitude,
    SgmaRestaurant.longitude,
    SgmaRestaurant.road_address,
    SgmaRestaurant.parcel_address,
)


def _browse_row_from_tuple(t: tuple) -> SgmaBrowseRow:
    return SgmaBrowseRow(
        id=int(t[0]),
        store_name=str(t[1] or ""),
        branch_name=str(t[2] or ""),
        biz_mid_name=str(t[3] or ""),
        biz_minor_name=str(t[4] or ""),
        ksic_name=str(t[5] or ""),
        biz_number=str(t[6] or ""),
        district=str(t[7] or ""),
        sigungu_name=str(t[8] or ""),
        latitude=t[9],
        longitude=t[10],
        road_address=str(t[11] or ""),
        parcel_address=str(t[12] or ""),
    )


def sgma_category_of(r: SgmaBrowseRow) -> tuple[str, str]:
    """앱 카테고리 슬러그·표시 라벨."""
    slug, inferred = classify_sgma_category(
        r.biz_mid_name, r.biz_minor_name, r.ksic_name
    )
    label = CATEGORY_LABEL_BY_SLUG.get(slug, inferred)
    return slug, label


def sgma_display_from_row(r: SgmaBrowseRow) -> str:
    """상호 표시 문자열."""
    s, b = (r.store_name or "").strip(), (r.branch_name or "").strip()
    if b:
        return f"{s} ({b})"
    return s or "상호 미상"


def score_sgma_for_topic(r: SgmaBrowseRow, topic_slug: str) -> int:
    raw = f"{topic_slug}:{r.id}:{r.biz_number}:{r.store_name}"
    return int(hashlib.md5(raw.encode("utf-8")).hexdigest()[:8], 16)


def pick_sgmas(
    pool: list[SgmaBrowseRow],
    topic_slug: str,
    *,
    limit: int,
) -> list[SgmaBrowseRow]:
    if not pool:
        return []
    ranked = sorted(pool, key=lambda r: score_sgma_for_topic(r, topic_slug))
    n = min(limit, len(ranked))
    offset = score_sgma_for_topic(ranked[0], f"off-{topic_slug}") % max(len(ranked), 1)
    rotated = ranked[offset:] + ranked[:offset]
    return rotated[:n]


def trending_sgma_boost(pool: list[SgmaBrowseRow]) -> list[SgmaBrowseRow]:
    """조회 통계 없이 상대적 ‘관심’ 순 흉내 — 업소번호 해시."""

    def key(r: SgmaBrowseRow) -> tuple[int, int]:
        h = hash(r.biz_number or str(r.id)) % 8192
        return (-abs(h), r.id)

    return sorted(pool, key=key)


def pick_mixed_sgma_by_category(
    pool: list[SgmaBrowseRow],
    topic_slug: str,
    *,
    limit: int,
) -> list[SgmaBrowseRow]:
    """주제 행 안에서 카테고리별로 균등에 가깝게."""
    if not pool:
        return []

    by_cat: dict[str, list[SgmaBrowseRow]] = defaultdict(list)
    for r in pool:
        by_cat[sgma_category_of(r)[0]].append(r)

    ranked: dict[str, list[SgmaBrowseRow]] = {
        cat: sorted(rs, key=lambda r: score_sgma_for_topic(r, topic_slug))
        for cat, rs in by_cat.items()
    }
    indices = {cat: 0 for cat in ranked}
    cats = list(ranked.keys())
    out: list[SgmaBrowseRow] = []
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


def sort_sgmas_by_distance(
    rows: list[SgmaBrowseRow],
    user_lat: float,
    user_lng: float,
) -> list[SgmaBrowseRow]:
    return sorted(
        rows,
        key=lambda r: distance_km_to_entity(r, user_lat, user_lng),
    )


def sgmas_to_card_summaries(
    rows: list[SgmaBrowseRow],
    *,
    user_lat: float | None = None,
    user_lng: float | None = None,
    with_rank: bool = False,
    with_category: bool = False,
) -> list[dict]:
    """목록 API용 — 이름·이미지·(선택) 구·거리·장르."""
    ordered = rows
    if user_lat is not None and user_lng is not None:
        ordered = sort_sgmas_by_distance(rows, user_lat, user_lng)

    items: list[dict] = []
    for i, r in enumerate(ordered, start=1):
        slug, label = sgma_category_of(r)
        nm = sgma_display_from_row(r)
        item: dict = {
            "id": r.id,
            "name": nm,
            "image_url": image_url_for_restaurant(nm, slug, ""),
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


def sgmas_to_pick_items(
    rows: list[SgmaBrowseRow],
    *,
    user_lat: float | None = None,
    user_lng: float | None = None,
) -> list[dict]:
    """하위 호환 — ``sgmas_to_card_summaries`` 와 동일(장르·순위 포함)."""
    return sgmas_to_card_summaries(
        rows,
        user_lat=user_lat,
        user_lng=user_lng,
        with_rank=True,
        with_category=True,
    )


def sgma_topic_row(
    topic: TopicDef,
    sgmas: list[SgmaBrowseRow],
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
        "restaurants": sgmas_to_card_summaries(
            sgmas,
            user_lat=user_lat,
            user_lng=user_lng,
            with_category=with_category_on_cards,
        ),
        "link_title": link_title,
    }


def bounded_sgma_slice(
    db: Session,
    *,
    limit_rows: int = 10_000,
    rotation_salt: int = 0,
    day_ord: int | None = None,
    total_row_count: int | None = None,
) -> list[SgmaBrowseRow]:
    """대량 ``restaurant`` 테이블용 — 필요 컬럼만 윈도우 조회."""
    do = day_ord if day_ord is not None else date.today().toordinal()
    if total_row_count is not None:
        cnt = int(total_row_count)
    else:
        cnt = int(
            db.execute(select(func.count()).select_from(SgmaRestaurant)).scalar_one()
            or 0
        )
    if cnt == 0:
        return []
    n = min(limit_rows, cnt)
    span = cnt - n
    off = ((do * 79_691 + rotation_salt * 3_961) % (span + 1)) if span > 0 else 0
    stmt = (
        select(*SGMA_BROWSE_COLUMNS)
        .order_by(SgmaRestaurant.id)
        .offset(off)
        .limit(n)
    )
    return [_browse_row_from_tuple(t) for t in db.execute(stmt).all()]


SGMA_TEXT_SEARCH_COLUMNS = (
    SgmaRestaurant.store_name,
    SgmaRestaurant.branch_name,
    SgmaRestaurant.biz_mid_name,
    SgmaRestaurant.biz_minor_name,
    SgmaRestaurant.ksic_name,
    SgmaRestaurant.district,
    SgmaRestaurant.sigungu_name,
    SgmaRestaurant.road_address,
    SgmaRestaurant.parcel_address,
)


def fetch_sgma_text_search_candidates(
    db: Session,
    *,
    patterns: list[str],
    limit: int = 1_600,
) -> list[SgmaBrowseRow]:
    """ILIKE 후보만 제한 행수로 로드(목록용 컬럼 projection)."""
    uniq: list[str] = []
    for p in patterns:
        if p and p not in uniq:
            uniq.append(p)
        if len(uniq) >= 14:
            break
    if not uniq:
        return bounded_sgma_slice(db, limit_rows=min(6_000, limit * 4))
    parts = [or_(*[col.ilike(p) for col in SGMA_TEXT_SEARCH_COLUMNS]) for p in uniq]
    cond = or_(*parts) if len(parts) > 1 else parts[0]
    stmt = select(*SGMA_BROWSE_COLUMNS).where(cond).limit(limit)
    rows = [_browse_row_from_tuple(t) for t in db.execute(stmt).all()]
    if not rows:
        return bounded_sgma_slice(db, limit_rows=min(8_000, limit * 5))
    return rows


def sgma_restaurant_name_for_views(db: Session, store_id: int) -> str | None:
    r = db.get(SgmaRestaurant, store_id)
    if r is None:
        return None
    return sgma_display_from_row(
        SgmaBrowseRow(
            id=r.id,
            store_name=r.store_name or "",
            branch_name=r.branch_name or "",
            biz_mid_name=r.biz_mid_name or "",
            biz_minor_name=r.biz_minor_name or "",
            ksic_name=r.ksic_name or "",
            biz_number=r.biz_number or "",
            district=r.district or "",
            sigungu_name=r.sigungu_name or "",
            latitude=r.latitude,
            longitude=r.longitude,
        )
    )
