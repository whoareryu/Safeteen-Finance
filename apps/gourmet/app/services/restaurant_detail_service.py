"""식당 상세 Facade — ``restaurants`` 단일 소스."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from apps.gourmet.app.adapters.restaurant_detail_adapter import OrmRestaurantDetailAdapter


class RestaurantDetailService:
    def __init__(self, adapter: OrmRestaurantDetailAdapter | None = None) -> None:
        self._adapter = adapter or OrmRestaurantDetailAdapter()

    def get_detail(self, db: Session, restaurant_id: int) -> dict[str, Any] | None:
        return self._adapter.get_detail(db, restaurant_id)

    def exists(self, db: Session, restaurant_id: int) -> bool:
        return self.get_detail(db, restaurant_id) is not None

    def display_name(self, db: Session, restaurant_id: int) -> str | None:
        detail = self.get_detail(db, restaurant_id)
        if detail is None:
            return None
        return str(detail.get("name") or "")
