from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant


class RestaurantUseCase(ABC):
    @abstractmethod
    def get_detail(self, db: Session, restaurant_id: int) -> Restaurant | None:
        pass

    @abstractmethod
    def list_category_page(
        self,
        db: Session,
        *,
        category_slug: str,
        offset: int,
        limit: int,
        district: str | None = None,
    ) -> tuple[list[Restaurant], int]:
        pass
