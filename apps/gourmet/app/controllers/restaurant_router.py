"""Restaurant 도메인 API (v2) — Controller."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from apps.gourmet.app.schemas.restaurant_schemas import (
    RestaurantCardV2,
    RestaurantCategoryListResponse,
    RestaurantDetailV2,
)
from apps.gourmet.app.services.restaurant_domain_service import RestaurantDomainService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gourmet/v2", tags=["gourmet-restaurants"])

_service = RestaurantDomainService()


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantDetailV2)
def read_restaurant_detail(
    restaurant_id: int,
    db: Session = Depends(get_sync_db),
) -> RestaurantDetailV2:
    row = _service.get_detail(db, restaurant_id)
    if row is None:
        raise HTTPException(status_code=404, detail="식당을 찾을 수 없습니다.")
    return RestaurantDetailV2(
        id=row.id,
        name=row.name,
        category_slug=row.category_slug,
        category_label=row.category_label,
        district=row.district,
        description=row.description,
        image_url=row.image_url,
        avg_price=row.avg_price,
        signature_menu=row.signature_menu,
        ai_tags=row.ai_tags or [],
        road_address=row.road_address,
        parcel_address=row.parcel_address,
        latitude=row.latitude,
        longitude=row.longitude,
        view_count=row.view_count,
    )


@router.get(
    "/categories/{category_slug}/restaurants",
    response_model=RestaurantCategoryListResponse,
)
def list_restaurants_by_category(
    category_slug: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    district: str | None = None,
    db: Session = Depends(get_sync_db),
) -> RestaurantCategoryListResponse:
    rows, total = _service.list_category_page(
        db,
        category_slug=category_slug,
        offset=offset,
        limit=limit,
        district=district,
    )
    cards = [RestaurantCardV2(**_service.to_card_dict(r)) for r in rows]
    return RestaurantCategoryListResponse(
        category_slug=category_slug,
        restaurants=cards,
        offset=offset,
        limit=limit,
        total=total,
        has_more=offset + len(cards) < total,
    )
