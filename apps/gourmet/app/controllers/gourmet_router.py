import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.database import DATABASE_INIT_ERROR, get_sync_db
from apps.gourmet.app.data.category_topics import ALL_CATEGORY_SLUGS
from apps.gourmet.app.schemas.gourmet_schemas import (
    CategoryBrowseResponse,
    HomeBrowseResponse,
    OffsetLimitPagination,
    RecordViewResponse,
    RestaurantDetailResponse,
    RestaurantSearchResponse,
    RestaurantViewStatResponse,
    SearchMatchedTopic,
    RestaurantCardSummary,
    TodayPicksResponse,
    TopicBrowsePagination,
    TopicMeta,
    TopicRowResponse,
)
from apps.gourmet.app.services.category_browse_service import (
    get_category_browse,
    list_topic_catalog,
)
from apps.gourmet.app.services.home_browse_service import get_home_browse
from apps.gourmet.app.services.sgma_browse_service import (
    sgma_restaurant_name_for_views,
    sgmas_to_card_summaries,
)
from apps.gourmet.app.services.restaurant_location_service import parse_user_location
from apps.gourmet.app.services.sgma_restaurant_service import sgma_restaurant_detail_dict
from apps.gourmet.app.services.restaurant_search_service import search_restaurants
from apps.gourmet.app.services.search_query_service import record_search_query
from apps.gourmet.app.services.today_picks_service import get_today_picks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gourmet", tags=["gourmet"])


def _effective_list_offset(*, limit: int, offset: int, page: int | None) -> int:
    """page(1-based)가 있으면 offset 대신 (page-1)*limit."""
    if page is not None:
        return (page - 1) * limit
    return offset


def _topic_rows_from_dicts(rows: list[dict]) -> list[TopicRowResponse]:
    return [
        TopicRowResponse(
            slug=r["slug"],
            title=r["title"],
            subtitle=r["subtitle"],
            emoji=r["emoji"],
            keywords=r["keywords"],
            restaurants=[RestaurantCardSummary(**item) for item in r["restaurants"]],
            category_slug=r.get("category_slug"),
            category_label=r.get("category_label"),
            link_title=r.get("link_title", True),
        )
        for r in rows
    ]


def _location_from_query(
    lat: float | None, lng: float | None
) -> tuple[float, float] | None:
    loc = parse_user_location(lat, lng)
    if lat is not None and lng is not None and loc is None:
        raise HTTPException(status_code=400, detail="위치 좌표가 올바르지 않습니다.")
    return loc


@router.get("/categories/{category_slug}/browse", response_model=CategoryBrowseResponse)
def read_category_browse(
    category_slug: str,
    q: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    topic_offset: int = Query(0, ge=0, le=5000),
    topic_limit: int = Query(4, ge=1, le=48),
    per_topic_limit: int = Query(10, ge=1, le=24),
    db: Session = Depends(get_sync_db),
):
    """카테고리별 주제 행 — 넷플릭스 스타일 맛집 안내."""
    if category_slug not in ALL_CATEGORY_SLUGS:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail="데이터베이스에 연결할 수 없습니다.")
    user_loc = _location_from_query(lat, lng)
    try:
        slug, label, rows, pagination_meta = get_category_browse(
            db,
            category_slug,
            q=q,
            user_lat=user_loc[0] if user_loc else None,
            user_lng=user_loc[1] if user_loc else None,
            topic_offset=topic_offset,
            topic_limit=topic_limit,
            per_topic_limit=per_topic_limit,
        )
    except Exception:
        logger.exception("[gourmet] category browse 실패 slug=%s", category_slug)
        raise HTTPException(
            status_code=500,
            detail="카테고리 맛집 목록을 불러오지 못했습니다.",
        ) from None
    topics = _topic_rows_from_dicts(rows)
    return CategoryBrowseResponse(
        category_slug=slug,
        category_label=label,
        query=q,
        topic_count=len(topics),
        topics=topics,
        nearby_mode=user_loc is not None,
        pagination=TopicBrowsePagination(**pagination_meta),
    )


@router.get("/home-browse", response_model=HomeBrowseResponse)
def read_home_browse(
    q: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    topic_offset: int = Query(0, ge=0, le=5000),
    topic_limit: int = Query(4, ge=1, le=48),
    per_topic_limit: int = Query(10, ge=1, le=24),
    db: Session = Depends(get_sync_db),
):
    """메인 — 전 카테고리 주제 추천을 섞어서 반환."""
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail="데이터베이스에 연결할 수 없습니다.")
    user_loc = _location_from_query(lat, lng)
    try:
        rows, pagination_meta = get_home_browse(
            db,
            q=q,
            user_lat=user_loc[0] if user_loc else None,
            user_lng=user_loc[1] if user_loc else None,
            topic_offset=topic_offset,
            topic_limit=topic_limit,
            per_topic_limit=per_topic_limit,
        )
    except Exception:
        logger.exception("[gourmet] home-browse 실패")
        raise HTTPException(
            status_code=500,
            detail="홈 맛집 목록을 불러오지 못했습니다.",
        ) from None
    topics = _topic_rows_from_dicts(rows)
    return HomeBrowseResponse(
        query=q,
        topic_count=len(topics),
        topics=topics,
        nearby_mode=user_loc is not None,
        pagination=TopicBrowsePagination(**pagination_meta),
    )


@router.get("/search", response_model=RestaurantSearchResponse)
def read_restaurant_search(
    q: str,
    lat: float | None = None,
    lng: float | None = None,
    offset: int = Query(0, ge=0, le=50_000),
    limit: int = Query(10, ge=1, le=50),
    page: int | None = Query(None, ge=1, le=10_000),
    db: Session = Depends(get_sync_db),
):
    """검색어에 맞는 맛집 추천 (메뉴·설명·주제 키워드)."""
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail="데이터베이스에 연결할 수 없습니다.")
    list_offset = _effective_list_offset(limit=limit, offset=offset, page=page)
    if not q.strip():
        return RestaurantSearchResponse(
            query="",
            summary="",
            matched_topics=[],
            restaurants=[],
            pagination=OffsetLimitPagination(
                offset=list_offset,
                limit=limit,
                total=0,
                has_more=False,
            ),
        )
    user_loc = _location_from_query(lat, lng)
    try:
        result = search_restaurants(
            db,
            q,
            user_lat=user_loc[0] if user_loc else None,
            user_lng=user_loc[1] if user_loc else None,
            offset=list_offset,
            limit=limit,
        )
    except Exception:
        logger.exception("[gourmet] search 실패 q=%s", q)
        raise HTTPException(
            status_code=500,
            detail="검색 결과를 불러오지 못했습니다.",
        ) from None
    try:
        record_search_query(
            db,
            result["query"],
            result_count=result.get("pagination", {}).get("total", len(result.get("restaurants") or [])),
        )
    except Exception:
        logger.exception("[gourmet] search log 저장 실패 q=%s", q)
        db.rollback()
    pag = result["pagination"]
    return RestaurantSearchResponse(
        query=result["query"],
        summary=result["summary"],
        matched_topics=[SearchMatchedTopic(**t) for t in result["matched_topics"]],
        restaurants=[RestaurantCardSummary(**item) for item in result["restaurants"]],
        nearby_mode=bool(result.get("nearby_mode")),
        pagination=OffsetLimitPagination(**pag),
    )


@router.get("/categories/{category_slug}/topics", response_model=list[TopicMeta])
def read_category_topic_catalog(category_slug: str):
    """주제 검색용 카탈로그."""
    if category_slug not in ALL_CATEGORY_SLUGS:
        raise HTTPException(status_code=404, detail="카테고리를 찾을 수 없습니다.")
    return [TopicMeta(**t) for t in list_topic_catalog(category_slug)]


@router.get("/today-picks", response_model=TodayPicksResponse)
def read_today_picks(
    lat: float | None = None,
    lng: float | None = None,
    offset: int = Query(0, ge=0, le=50_000),
    limit: int = Query(24, ge=1, le=50),
    page: int | None = Query(None, ge=1, le=10_000),
    db: Session = Depends(get_sync_db),
):
    """오늘의 맛집 — 카테고리별 2~3곳(SgmaRestaurant, 날짜 시드)."""
    if DATABASE_INIT_ERROR:
        raise HTTPException(
            status_code=503,
            detail="데이터베이스에 연결할 수 없습니다.",
        )
    user_loc = _location_from_query(lat, lng)
    list_offset = _effective_list_offset(limit=limit, offset=offset, page=page)
    try:
        pick_date, picked_rows = get_today_picks(
            db,
            user_lat=user_loc[0] if user_loc else None,
            user_lng=user_loc[1] if user_loc else None,
        )
    except Exception:
        logger.exception("[gourmet] today-picks 생성 실패")
        raise HTTPException(
            status_code=500,
            detail="오늘의 맛집 목록을 불러오지 못했습니다.",
        ) from None

    pick_items = sgmas_to_card_summaries(
        picked_rows,
        user_lat=user_loc[0] if user_loc else None,
        user_lng=user_loc[1] if user_loc else None,
        with_rank=True,
        with_category=True,
    )
    total = len(pick_items)
    slice_end = list_offset + limit
    sliced = pick_items[list_offset:slice_end]
    title = "내 주변 오늘의 맛집" if user_loc else "오늘의 맛집"
    return TodayPicksResponse(
        title=title,
        date=pick_date.isoformat(),
        picks=[RestaurantCardSummary(**item) for item in sliced],
        nearby_mode=user_loc is not None,
        pagination=OffsetLimitPagination(
            offset=list_offset,
            limit=limit,
            total=total,
            has_more=slice_end < total,
        ),
    )


@router.get("/official-store/{store_id}", response_model=RestaurantDetailResponse)
def read_official_store_detail(store_id: int, db: Session = Depends(get_sync_db)):
    """공공데이터 ``restaurant`` 테이블(SgmaRestaurant) 상세."""
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail="데이터베이스에 연결할 수 없습니다.")
    from apps.gourmet.app.models.sgma_restaurant import SgmaRestaurant

    row = db.get(SgmaRestaurant, store_id)
    if row is None:
        raise HTTPException(status_code=404, detail="상가 정보를 찾을 수 없습니다.")
    return RestaurantDetailResponse(**sgma_restaurant_detail_dict(row))


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantDetailResponse)
def read_restaurant_detail(restaurant_id: int, db: Session = Depends(get_sync_db)):
    """``restaurant`` 테이블(SgmaRestaurant) 매장 상세."""
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail="데이터베이스에 연결할 수 없습니다.")
    from apps.gourmet.app.models.sgma_restaurant import SgmaRestaurant

    row = db.get(SgmaRestaurant, restaurant_id)
    if row is None:
        raise HTTPException(status_code=404, detail="식당을 찾을 수 없습니다.")
    return RestaurantDetailResponse(**sgma_restaurant_detail_dict(row))


@router.post("/restaurants/{restaurant_id}/view", response_model=RecordViewResponse)
def post_restaurant_view(restaurant_id: int, db: Session = Depends(get_sync_db)):
    """레거시 호환 — 조회 집계는 사용하지 않음(항상 0)."""
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail="데이터베이스에 연결할 수 없습니다.")
    from apps.gourmet.app.models.sgma_restaurant import SgmaRestaurant

    if db.get(SgmaRestaurant, restaurant_id) is None:
        raise HTTPException(status_code=404, detail="식당을 찾을 수 없습니다.")
    return RecordViewResponse(
        restaurant_id=restaurant_id,
        view_count=0,
        message="조회 집계는 지원하지 않습니다.",
    )


@router.get("/restaurants/{restaurant_id}/views", response_model=RestaurantViewStatResponse)
def read_restaurant_views(restaurant_id: int, db: Session = Depends(get_sync_db)):
    """조회 수는 항상 0 (legacy API)."""
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail="데이터베이스에 연결할 수 없습니다.")
    name = sgma_restaurant_name_for_views(db, restaurant_id)
    if name is None:
        raise HTTPException(status_code=404, detail="식당을 찾을 수 없습니다.")
    return RestaurantViewStatResponse(
        restaurant_id=restaurant_id,
        restaurant_name=name,
        view_count=0,
        first_viewed_at=None,
        last_viewed_at=None,
    )


@router.get("/view-stats", response_model=list[RestaurantViewStatResponse])
def read_top_view_stats(db: Session = Depends(get_sync_db), limit: int = 20):
    """레거시 — 시드 전용 조회 통계 제거로 빈 목록."""
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail="데이터베이스에 연결할 수 없습니다.")
    _ = min(limit, 100)
    return []
