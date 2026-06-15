"""식당 상세 Facade — ``restaurants`` 단일 소스."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from restaurant.adapter.outbound.http.restaurant_detail_adapter import OrmRestaurantDetailAdapter
from restaurant.adapter.inbound.api.schemas.restaurant_detail_schema import RestaurantDetailSchema
from restaurant.app.dtos.restaurant_detail_dto import RestaurantDetailResponse
from restaurant.app.ports.input.restaurant_detail_use_case import RestaurantDetailUseCase
from restaurant.app.ports.output.restaurant_detail_repository import RestaurantDetailRepository


class RestaurantDetailInteractor(RestaurantDetailUseCase):
    def __init__(
        self,
        adapter: OrmRestaurantDetailAdapter | None = None,
        repository: RestaurantDetailRepository | None = None,
    ) -> None:
        self._adapter = adapter or OrmRestaurantDetailAdapter()
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

    async def introduce_myself(self, schema: RestaurantDetailSchema) -> RestaurantDetailResponse:
        return RestaurantDetailResponse(id=schema.id, name=schema.name)
