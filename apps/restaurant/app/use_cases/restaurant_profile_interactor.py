"""식당 상세 컬럼 스키마·프로필 동기화."""

from __future__ import annotations

import logging

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from restaurant.data.restaurant_images import image_url_for_restaurant
from restaurant.data.restaurant_profile_enrich import build_profile
from restaurant.data.seed_restaurants import SEED_RESTAURANTS
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.app.ports.input.restaurant_profile_use_case import RestaurantProfileUseCase
from restaurant.adapter.inbound.api.schemas.restaurant_profile_schema import RestaurantProfileSchema
from restaurant.app.dtos.restaurant_profile_dto import RestaurantProfileQuery, RestaurantProfileResponse
from restaurant.app.ports.output.restaurant_profile_repository import RestaurantProfileRepository


logger = logging.getLogger(__name__)


def ensure_restaurant_detail_schema(db: Session) -> None:
    """PostgreSQL — 상세 컬럼이 없으면 추가."""
    stmts = [
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS address VARCHAR(256)",
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS opening_hours VARCHAR(256)",
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS phone VARCHAR(32)",
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS instagram_url VARCHAR(512)",
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS reservation_available BOOLEAN DEFAULT false",
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS reservation_note VARCHAR(256)",
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS menu_items JSONB DEFAULT '[]'::jsonb",
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS latitude DOUBLE PRECISION",
        "ALTER TABLE restaurants ADD COLUMN IF NOT EXISTS longitude DOUBLE PRECISION",
    ]
    for stmt in stmts:
        db.execute(text(stmt))
    db.commit()


def sync_restaurant_profiles(db: Session) -> None:
    """기존 매장에 메뉴·주소·연락처가 비어 있으면 채움."""
    ensure_restaurant_detail_schema(db)
    restaurants = list(db.execute(select(Restaurant)).scalars().all())
    seed_by_name = {r["name"]: r for r in SEED_RESTAURANTS}
    updated = 0

    for r in restaurants:
        if r.address and r.menu_items:
            continue
        seed_row = seed_by_name.get(r.name)
        if seed_row and seed_row.get("address"):
            profile = {
                "address": seed_row.get("address", ""),
                "opening_hours": seed_row.get("opening_hours", ""),
                "phone": seed_row.get("phone"),
                "instagram_url": seed_row.get("instagram_url"),
                "reservation_available": seed_row.get("reservation_available", False),
                "reservation_note": seed_row.get("reservation_note", ""),
                "menu_items": seed_row.get("menu_items", []),
            }
        else:
            profile = build_profile(r.name, r.district, r.category_slug)

        r.address = profile.get("address") or r.address or ""
        r.opening_hours = profile.get("opening_hours") or r.opening_hours or ""
        r.phone = profile.get("phone") or r.phone
        r.instagram_url = profile.get("instagram_url") or r.instagram_url
        r.reservation_available = bool(
            profile.get("reservation_available", r.reservation_available)
        )
        r.reservation_note = profile.get("reservation_note") or r.reservation_note or ""
        if not r.menu_items:
            r.menu_items = profile.get("menu_items") or []
        updated += 1

    if updated:
        db.commit()
        logger.info("[gourmet] restaurant profiles 동기화 %s건", updated)


def sync_restaurant_images(db: Session) -> None:
    """전 매장 대표 이미지를 장르·메뉴 키워드에 맞게 갱신."""
    restaurants = list(db.execute(select(Restaurant)).scalars().all())
    updated = 0
    for r in restaurants:
        new_url = image_url_for_restaurant(
            r.name,
            r.category_slug,
            r.description or "",
            menu_items=list(r.menu_items or []),
        )
        if r.image_url != new_url:
            r.image_url = new_url
            updated += 1
    if updated:
        db.commit()
        logger.info("[gourmet] restaurant images 동기화 %s건", updated)


class RestaurantProfileInteractor(RestaurantProfileUseCase):
    def __init__(self, repository: RestaurantProfileRepository) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: RestaurantProfileSchema) -> RestaurantProfileResponse:
        return await self.repository.introduce_myself(
            RestaurantProfileQuery(id=schema.id, name=schema.name)
        )
