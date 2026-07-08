from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from restaurant.app.dtos.restaurant_browse_dto import RestaurantBrowseRow


class IRestaurantBrowseRepository(ABC):
    @abstractmethod
    def count_restaurants(
        self, db: Session, *, category_slug: str | None = None
    ) -> int: ...

    @abstractmethod
    def bounded_slice(
        self,
        db: Session,
        *,
        limit_rows: int = 10_000,
        rotation_salt: int = 0,
        day_ord: int | None = None,
        total_row_count: int | None = None,
        category_slug: str | None = None,
    ) -> list[RestaurantBrowseRow]: ...

    @abstractmethod
    def fetch_text_search_candidates(
        self,
        db: Session,
        *,
        patterns: list[str],
        limit: int = 1_600,
    ) -> list[RestaurantBrowseRow]: ...

    @abstractmethod
    def display_name_by_id(self, db: Session, store_id: int) -> str | None: ...
