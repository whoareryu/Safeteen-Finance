"""식당 latitude/longitude 동기화."""

from __future__ import annotations

import logging

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.app.use_cases.restaurant_location_interactor import coords_for_district

logger = logging.getLogger(__name__)


def ensure_restaurant_coordinate_schema(db: Session) -> None:
    db.execute(
        text(
            "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION"
        )
    )
    db.execute(
        text(
            "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION"
        )
    )
    db.commit()


def sync_restaurant_coordinates(db: Session) -> None:
    """전 매장 좌표를 상권 기준으로 채움."""
    ensure_restaurant_coordinate_schema(db)
    restaurants = list(db.execute(select(Restaurant)).scalars().all())
    updated = 0
    for r in restaurants:
        lat, lng = coords_for_district(r.district, r.id)
        if r.latitude != lat or r.longitude != lng:
            r.latitude = lat
            r.longitude = lng
            updated += 1
    if updated:
        db.commit()
        logger.info("[gourmet] restaurant coordinates 동기화 %s건", updated)
