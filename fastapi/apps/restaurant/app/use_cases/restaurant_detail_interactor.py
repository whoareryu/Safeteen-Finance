"""식당 상세 Facade — ``restaurants`` 단일 소스."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import Session

from restaurant.app.ports.input.restaurant_detail_use_case import RestaurantDetailUseCase
from restaurant.app.ports.output.restaurant_detail_repository import RestaurantDetailRepository

if TYPE_CHECKING:
    from restaurant.adapter.outbound.http.restaurant_detail_adapter import OrmRestaurantDetailAdapter


class RestaurantDetailInteractor(RestaurantDetailUseCase):
    def __init__(
        self,
        adapter: OrmRestaurantDetailAdapter | None = None,
        repository: RestaurantDetailRepository | None = None,
    ) -> None:
        if adapter is None:
            from restaurant.adapter.outbound.http.restaurant_detail_adapter import OrmRestaurantDetailAdapter
            adapter = OrmRestaurantDetailAdapter()
        self._adapter = adapter
        self._repository = repository

    def get_detail(self, db: Session, restaurant_id: int) -> dict[str, Any] | None:
        return self._adapter.get_detail(db, restaurant_id)

    def exists(self, db: Session, restaurant_id: int) -> bool:
        return self.get_detail(db, restaurant_id) is not None

    def display_name(self, db: Session, restaurant_id: int) -> str | None:
        detail = self.get_detail(db, restaurant_id)
        if detail is None:
            return None
        return str(detail.get("name") or "")

