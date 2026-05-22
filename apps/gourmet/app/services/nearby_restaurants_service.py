"""사용자 좌표 기준 주변 맛집."""

from __future__ import annotations

from sqlalchemy.orm import Session

from apps.gourmet.app.services.restaurant_browse_service import (
    RestaurantBrowseRow,
    bounded_restaurant_slice,
    rows_to_card_summaries,
)
from apps.gourmet.app.services.restaurant_location_service import distance_km_to_entity

NEARBY_POOL = 8_000


def list_nearby_restaurants(
    db: Session,
    *,
    lat: float,
    lng: float,
    radius_km: float = 3.0,
    category_slug: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> tuple[list[dict], dict]:
    pool = bounded_restaurant_slice(
        db,
        limit_rows=NEARBY_POOL,
        category_slug=category_slug,
    )
    with_dist: list[tuple[RestaurantBrowseRow, float]] = []
    for r in pool:
        d = distance_km_to_entity(r, lat, lng)
        if d <= radius_km:
            with_dist.append((r, d))

    with_dist.sort(key=lambda x: x[1])
    total = len(with_dist)
    page = with_dist[offset : offset + limit]
    rows = [r for r, _ in page]
    cards = rows_to_card_summaries(rows, user_lat=lat, user_lng=lng, with_category=True)
    for card, (_, dist) in zip(cards, page, strict=False):
        card["distance_km"] = round(dist, 1)

    return cards, {
        "offset": offset,
        "limit": limit,
        "total": total,
        "has_more": offset + len(cards) < total,
    }
