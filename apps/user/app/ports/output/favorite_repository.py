from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from user.adapter.outbound.orm.favorite_orm import Favorite


class FavoriteRepository(ABC):
    @abstractmethod
    def resolve_restaurant_id(self, db: Session, store_id: int) -> int | None:
        pass

    @abstractmethod
    def toggle(
        self, db: Session, *, user_id: int, restaurant_id: int
    ) -> bool:
        """True=추가, False=제거."""
        pass

    @abstractmethod
    def list_favorites(self, db: Session, user_id: int) -> list[Favorite]:
        pass

    @abstractmethod
    def is_favorited(
        self, db: Session, *, user_id: int, restaurant_id: int
    ) -> bool:
        pass

    @abstractmethod
    def list_restaurant_ids(self, db: Session, user_id: int) -> list[int]:
        pass
