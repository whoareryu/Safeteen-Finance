"""Restaurant 조회 시 관계 로딩 (캡슐화·N+1 방지)."""

from __future__ import annotations

from sqlalchemy.orm import joinedload, selectinload

from gourmet.adapter.outbound.orm.restaurant import Restaurant
from gourmet.adapter.outbound.orm.restaurant_tag import RestaurantTag

RESTAURANT_CARD_LOADS = (
    joinedload(Restaurant.category),
    joinedload(Restaurant.sigungu),
    joinedload(Restaurant.biz_classification),
    joinedload(Restaurant.price),
    selectinload(Restaurant.menus),
    selectinload(Restaurant.tag_links).joinedload(RestaurantTag.tag),
)

RESTAURANT_DETAIL_LOADS = RESTAURANT_CARD_LOADS + (
    joinedload(Restaurant.contact),
    selectinload(Restaurant.operating_hours),
)
