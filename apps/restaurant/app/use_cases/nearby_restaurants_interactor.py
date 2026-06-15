"""사용자 좌표 기준 주변 맛집."""

from __future__ import annotations

from sqlalchemy.orm import Session

from restaurant.app.use_cases.restaurant_browse_interactor import (
    RestaurantBrowseRow,
    bounded_restaurant_slice,
    rows_to_card_summaries,
)
from restaurant.app.use_cases.restaurant_location_interactor import distance_km_to_entity
from restaurant.app.ports.input.nearby_restaurants_use_case import NearbyRestaurantsUseCase
from restaurant.adapter.inbound.api.schemas.nearby_restaurants_schema import NearbyRestaurantsSchema
from restaurant.app.dtos.nearby_restaurants_dto import NearbyRestaurantsQuery, NearbyRestaurantsResponse
from restaurant.app.ports.output.nearby_restaurants_repository import NearbyRestaurantsRepository


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


class NearbyRestaurantsInteractor(NearbyRestaurantsUseCase):
    def __init__(self, repository: NearbyRestaurantsRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: NearbyRestaurantsSchema) -> NearbyRestaurantsResponse:
        return await self.repository.introduce_myself(
            NearbyRestaurantsQuery(id=schema.id, name=schema.name)
        )
