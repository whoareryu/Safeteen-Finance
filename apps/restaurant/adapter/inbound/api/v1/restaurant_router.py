"""Restaurant 도메인 API (v2) — Controller."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.database import get_sync_db
from restaurant.adapter.inbound.api.schemas.restaurant_schema import (
    RestaurantCardV2,
    RestaurantCategoryListResponse,
    RestaurantDetailV2,
)
from restaurant.app.ports.input.restaurant_use_case import RestaurantUseCase
from restaurant.dependencies.restaurant_provider import get_restaurant_use_case

router = APIRouter(prefix="/gourmet/v2", tags=["gourmet-restaurants"])


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantDetailV2)
def read_restaurant_detail(
    restaurant_id: int,
    db: Session = Depends(get_sync_db),
    service: RestaurantUseCase = Depends(get_restaurant_use_case),
) -> RestaurantDetailV2:
    row = service.get_detail(db, restaurant_id)
    detail = row.to_detail_dict()
    return RestaurantDetailV2(
        id=detail["id"],
        name=detail["name"],
        category_slug=detail["category_slug"],
        category_label=detail["category_label"],
        district=detail["district"],
        description=detail.get("description", ""),
        image_url=detail.get("image_url", ""),
        avg_price=detail.get("avg_price"),
        signature_menu=detail.get("signature_menu", ""),
        ai_tags=detail.get("ai_tags", []),
        road_address=detail.get("road_address", ""),
        parcel_address=detail.get("parcel_address", ""),
        latitude=detail.get("latitude"),
        longitude=detail.get("longitude"),
        view_count=detail.get("view_count", 0),
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
    service: RestaurantUseCase = Depends(get_restaurant_use_case),
) -> RestaurantCategoryListResponse:
    rows, total = service.list_category_page(
        db,
        category_slug=category_slug,
        offset=offset,
        limit=limit,
        district=district,
    )
    cards = [RestaurantCardV2(**service.to_card_dict(r)) for r in rows]
    return RestaurantCategoryListResponse(
        category_slug=category_slug,
        restaurants=cards,
        offset=offset,
        limit=limit,
        total=total,
        has_more=offset + len(cards) < total,
    )
