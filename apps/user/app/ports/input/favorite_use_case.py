from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from apps.friday_13th.auth.user_model import User
from user.app.dtos.favorite_dto import FavoriteCheckQuery, FavoriteToggleCommand


class FavoriteUseCase(ABC):
    @abstractmethod
    def toggle(
        self, db: Session, user: User, command: FavoriteToggleCommand
    ) -> tuple[bool, str]:
        pass

    @abstractmethod
    def list_cards(self, db: Session, user_id: int) -> list[dict]:
        pass

    @abstractmethod
    def favorited_store_ids(self, db: Session, query: FavoriteCheckQuery) -> list[int]:
        pass

    @abstractmethod
    def all_favorited_store_ids_for_user(self, db: Session, user_id: int) -> list[int]:
        pass

    @abstractmethod
    async def introduce_myself(self, schema) -> "FavoriteResponse":
        pass
