"""식당 상세 Adapter — ``restaurants`` 테이블."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.pg.restaurant_pg_repository import RestaurantRepository


class RestaurantDetailAdapter(ABC):
    @abstractmethod
    def get_detail(self, db: Session, restaurant_id: int) -> dict[str, Any] | None:
        raise NotImplementedError

    @property
    @abstractmethod
    def priority(self) -> int:
        raise NotImplementedError


class OrmRestaurantDetailAdapter(RestaurantDetailAdapter):
    def __init__(self, repo: RestaurantRepository | None = None) -> None:
        self._repo = repo or RestaurantRepository()

    @property
    def priority(self) -> int:
        return 0

    def get_detail(self, db: Session, restaurant_id: int) -> dict[str, Any] | None:
        row: Restaurant | None = self._repo.get_by_id(db, restaurant_id)
        return row.to_detail_dict() if row else None
