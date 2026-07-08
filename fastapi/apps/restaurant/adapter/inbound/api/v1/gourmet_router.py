from __future__ import annotations

import random

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from restaurant.adapter.inbound.api.schemas.gourmet_schema import RestaurantDetailResponse
from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.data.category_topics import home_feed_topics
from restaurant.dependencies.restaurant_detail_provider import get_restaurant_detail_use_case
from restaurant.app.use_cases.restaurant_detail_interactor import RestaurantDetailInteractor

router = APIRouter(prefix="/gourmet", tags=["gourmet"])

_TOPIC_ROWS = 5       # 메인 홈에 보여줄 주제 행 수
_PER_TOPIC = 5        # 행당 식당 수
_CANDIDATE_RADIUS = 200  # 위치 기반 후보 풀 크기


def _topic_restaurants(
    db: Session,
    category_slugs: tuple[str, ...],
    *,
    lat: float | None,
    lng: float | None,
    limit: int,
) -> list[dict]:
    """주제에 맞는 식당 limit개 반환 — 위치 제공 시 가까운 순."""
    stmt = (
        select(
            Restaurant.id,
            Restaurant.name,
            Restaurant.road_address,
            Restaurant.latitude,
            Restaurant.longitude,
            FoodCategory.slug,
            FoodCategory.label,
        )
        .join(FoodCategory, Restaurant.category_id == FoodCategory.id)
        .where(Restaurant.latitude.is_not(None))
    )
    if category_slugs:
        stmt = stmt.where(FoodCategory.slug.in_(category_slugs))

    if lat is not None and lng is not None:
        dlat = (Restaurant.latitude - lat) * 111.0
        dlng = (Restaurant.longitude - lng) * 88.0
        dist_sq = func.power(dlat, 2) + func.power(dlng, 2)
        stmt = stmt.order_by(dist_sq).limit(limit)
    else:
        stmt = stmt.order_by(FoodCategory.slug, Restaurant.id % 997).limit(limit)

    return [
        {
            "id": row.id,
            "name": row.name,
            "genre": row.label,
            "road_address": row.road_address or "",
            "latitude": row.latitude,
            "longitude": row.longitude,
        }
        for row in db.execute(stmt).all()
    ]


@router.get("/topics/feed")
def get_topics_feed(
    lat: float | None = None,
    lng: float | None = None,
    n: int = _TOPIC_ROWS,
    db: Session = Depends(get_sync_db),
) -> list[dict]:
    """메인 홈 넷플릭스형 주제별 추천 — n개 행, 각 5곳, 위치 기반 가까운 순."""
    topics = home_feed_topics()
    random.shuffle(topics)
    result: list[dict] = []
    for topic in topics:
        if len(result) >= n:
            break
        restaurants = _topic_restaurants(
            db,
            topic.category_slugs,
            lat=lat,
            lng=lng,
            limit=_PER_TOPIC,
        )
        if len(restaurants) < 2:
            continue
        result.append(
            {
                "slug": topic.slug,
                "title": topic.title,
                "subtitle": topic.subtitle,
                "emoji": topic.emoji,
                "restaurants": restaurants,
            }
        )
    return result


@router.get("/official-store/{store_id}", response_model=RestaurantDetailResponse)
def read_official_store_detail(
    store_id: int,
    db: Session = Depends(get_sync_db),
    detail_service: RestaurantDetailInteractor = Depends(get_restaurant_detail_use_case),
):
    """공공·정제 테이블 통합 상세 (Adapter 체인)."""
    detail = detail_service.get_detail(db, store_id)
    return RestaurantDetailResponse(**detail)


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantDetailResponse)
def read_restaurant_detail(
    restaurant_id: int,
    db: Session = Depends(get_sync_db),
    detail_service: RestaurantDetailInteractor = Depends(get_restaurant_detail_use_case),
):
    """식당 상세 — ``RestaurantDetailInteractor`` (다형 Adapter)."""
    detail = detail_service.get_detail(db, restaurant_id)
    return RestaurantDetailResponse(**detail)
