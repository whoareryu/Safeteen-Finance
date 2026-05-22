"""카탈로그·주제·주변·검색 제안·보강 API."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.database import DATABASE_INIT_ERROR, get_sync_db
from apps.gourmet.app.schemas.catalog_schemas import (
    FoodCategoryItem,
    NearbyRestaurantsResponse,
    RestaurantEnrichmentResponse,
    RestaurantMenuItem,
    RestaurantMenusResponse,
    SearchSuggestResponse,
    SearchSuggestionItem,
    TopicMetaBrief,
    TopicRestaurantsResponse,
)
from apps.gourmet.app.schemas.gourmet_schemas import (
    OffsetLimitPagination,
    RestaurantCardSummary,
)
from apps.gourmet.app.services.category_catalog_service import list_food_categories
from apps.gourmet.app.services.nearby_restaurants_service import list_nearby_restaurants
from apps.gourmet.app.services.restaurant_enrichment_service import get_restaurant_enrichment
from apps.gourmet.app.services.restaurant_menu_service import get_restaurant_menus
from apps.gourmet.app.services.restaurant_location_service import parse_user_location
from apps.gourmet.app.services.search_suggest_service import suggest_search
from apps.gourmet.app.services.topic_restaurants_service import get_topic_restaurants

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gourmet", tags=["gourmet-catalog"])


def _db_ok() -> None:
    if DATABASE_INIT_ERROR:
        raise HTTPException(status_code=503, detail="데이터베이스에 연결할 수 없습니다.")


def _location_from_query(
    lat: float | None, lng: float | None
) -> tuple[float, float] | None:
    loc = parse_user_location(lat, lng)
    if lat is not None and lng is not None and loc is None:
        raise HTTPException(status_code=400, detail="위치 좌표가 올바르지 않습니다.")
    return loc


@router.get("/categories", response_model=list[FoodCategoryItem])
def read_food_categories(db: Session = Depends(get_sync_db)):
    """2NF ``food_categories`` 마스터."""
    _db_ok()
    return [FoodCategoryItem(**item) for item in list_food_categories(db)]


@router.get(
    "/restaurants/{restaurant_id}/menus",
    response_model=RestaurantMenusResponse,
)
def read_restaurant_menus(
    restaurant_id: int,
    db: Session = Depends(get_sync_db),
):
    """2NF ``restaurant_menus`` 목록."""
    _db_ok()
    payload = get_restaurant_menus(db, restaurant_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="식당을 찾을 수 없습니다.")
    return RestaurantMenusResponse(
        restaurant_id=payload["restaurant_id"],
        menus=[RestaurantMenuItem(**m) for m in payload["menus"]],
        signature_menu=payload["signature_menu"],
    )


@router.get(
    "/topics/{topic_slug}/restaurants",
    response_model=TopicRestaurantsResponse,
)
def read_topic_restaurants(
    topic_slug: str,
    lat: float | None = None,
    lng: float | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_sync_db),
):
    """주제 한 줄에 대한 맛집 목록(페이지네이션)."""
    _db_ok()
    user_loc = _location_from_query(lat, lng)
    try:
        result = get_topic_restaurants(
            db,
            topic_slug,
            user_lat=user_loc[0] if user_loc else None,
            user_lng=user_loc[1] if user_loc else None,
            offset=offset,
            limit=limit,
        )
    except Exception:
        logger.exception("[gourmet] topic restaurants slug=%s", topic_slug)
        raise HTTPException(
            status_code=500,
            detail="주제별 맛집 목록을 불러오지 못했습니다.",
        ) from None
    if result is None:
        raise HTTPException(status_code=404, detail="주제를 찾을 수 없습니다.")
    topic, cards, meta = result
    return TopicRestaurantsResponse(
        topic=TopicMetaBrief(
            slug=topic.slug,
            title=topic.title,
            subtitle=topic.subtitle,
            emoji=topic.emoji,
            keywords=list(topic.keywords),
            category_slugs=list(topic.category_slugs),
        ),
        restaurants=[RestaurantCardSummary(**c) for c in cards],
        nearby_mode=user_loc is not None,
        pagination=OffsetLimitPagination(**meta),
    )


@router.get("/nearby", response_model=NearbyRestaurantsResponse)
def read_nearby_restaurants(
    lat: float = Query(..., description="위도"),
    lng: float = Query(..., description="경도"),
    radius_km: float = Query(3.0, ge=0.5, le=30.0),
    category_slug: str | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_sync_db),
):
    """반경(km) 내 맛집 — 거리순."""
    _db_ok()
    loc = _location_from_query(lat, lng)
    if loc is None:
        raise HTTPException(status_code=400, detail="위치 좌표가 올바르지 않습니다.")
    try:
        cards, meta = list_nearby_restaurants(
            db,
            lat=loc[0],
            lng=loc[1],
            radius_km=radius_km,
            category_slug=category_slug,
            offset=offset,
            limit=limit,
        )
    except Exception:
        logger.exception("[gourmet] nearby lat=%s lng=%s", lat, lng)
        raise HTTPException(
            status_code=500,
            detail="주변 맛집을 불러오지 못했습니다.",
        ) from None
    return NearbyRestaurantsResponse(
        latitude=loc[0],
        longitude=loc[1],
        radius_km=radius_km,
        restaurants=[RestaurantCardSummary(**c) for c in cards],
        pagination=OffsetLimitPagination(**meta),
    )


@router.get("/search/suggest", response_model=SearchSuggestResponse)
def read_search_suggest(
    q: str = Query("", max_length=64),
    limit: int = Query(12, ge=1, le=30),
    db: Session = Depends(get_sync_db),
):
    """검색 자동완성 — 로그·주제·추천 칩."""
    _db_ok()
    items = suggest_search(db, q, limit=limit)
    return SearchSuggestResponse(
        query=q,
        suggestions=[SearchSuggestionItem(**i) for i in items],
    )


@router.get(
    "/restaurants/{restaurant_id}/enrichment",
    response_model=RestaurantEnrichmentResponse,
)
def read_restaurant_enrichment(
    restaurant_id: int,
    db: Session = Depends(get_sync_db),
):
    """외부 보강 필드 조회(배치 적재 연동 전 스텁·소스 상태 포함)."""
    _db_ok()
    payload = get_restaurant_enrichment(db, restaurant_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="식당을 찾을 수 없습니다.")
    from apps.gourmet.app.schemas.catalog_schemas import EnrichmentSourceStatus

    sources = {
        k: EnrichmentSourceStatus(**v) for k, v in payload.get("sources", {}).items()
    }
    return RestaurantEnrichmentResponse(
        restaurant_id=payload["restaurant_id"],
        phone=payload.get("phone"),
        opening_hours=payload.get("opening_hours"),
        closed_weekdays_label=payload.get("closed_weekdays_label"),
        instagram_url=payload.get("instagram_url"),
        extra_images=payload.get("extra_images") or [],
        sources=sources,
        message=payload.get("message", ""),
    )
