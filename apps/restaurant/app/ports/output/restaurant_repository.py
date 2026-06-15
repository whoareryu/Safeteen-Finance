from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant


class IRestaurantRepository(ABC):
    @abstractmethod
    def get_by_id(self, db: Session, restaurant_id: int) -> Restaurant | None:
        pass

    @abstractmethod
    def bulk_insert(
        self, db: Session, rows: list[Restaurant], *, commit: bool = True
    ) -> int:
        pass

    @abstractmethod
    def delete_all(self, db: Session) -> int:
        pass

    @abstractmethod
    def list_by_category(
        self,
        db: Session,
        *,
        category_slug: str,
        offset: int,
        limit: int,
        district: str | None = None,
    ) -> list[Restaurant]:
        pass

    @abstractmethod
    def list_within_budget(
        self,
        db: Session,
        *,
        max_avg_price: int,
        category_slug: str | None,
        offset: int,
        limit: int,
    ) -> list[Restaurant]:
        pass

    @abstractmethod
    def count_by_category(
        self, db: Session, *, category_slug: str, district: str | None = None
    ) -> int:
        pass
