from __future__ import annotations

from sqlalchemy.orm import Session

from apps.friday_13th.auth.user_model import User
from user.app.dtos.favorite_dto import FavoriteCheckQuery, FavoriteResponse, FavoriteToggleCommand
from user.app.ports.input.favorite_use_case import FavoriteUseCase
from user.app.ports.output.favorite_repository import FavoriteRepository


class FavoriteInteractor(FavoriteUseCase):
    def __init__(self, repository: FavoriteRepository) -> None:
        self._repository = repository

    def toggle(
        self, db: Session, user: User, command: FavoriteToggleCommand
    ) -> tuple[bool, str]:
        rid = self._repository.resolve_restaurant_id(db, command.store_id)
        if rid is None:
            raise ValueError("매장을 찾을 수 없습니다.")
        added = self._repository.toggle(db, user_id=user.id, restaurant_id=rid)
        if added:
            return True, "즐겨찾기에 추가했습니다."
        return False, "즐겨찾기에서 제거했습니다."

    def list_cards(self, db: Session, user_id: int) -> list[dict]:
        out: list[dict] = []
        for fav in self._repository.list_favorites(db, user_id):
            r = fav.restaurant
            out.append(
                {
                    "store_id": r.id,
                    "restaurant_id": r.id,
                    "name": r.display_name(),
                    "image_url": r.image_url or "",
                    "district": r.district or "",
                    "category_slug": r.category_slug,
                    "category_label": r.category_label,
                    "signature_menu": r.signature_menu or "",
                }
            )
        return out

    def favorited_store_ids(self, db: Session, query: FavoriteCheckQuery) -> list[int]:
        favorited: list[int] = []
        for sid in query.store_ids:
            rid = self._repository.resolve_restaurant_id(db, sid)
            if rid is None:
                continue
            if self._repository.is_favorited(
                db, user_id=query.user_id, restaurant_id=rid
            ):
                favorited.append(sid)
        return favorited

    def all_favorited_store_ids_for_user(self, db: Session, user_id: int) -> list[int]:
        return self._repository.list_restaurant_ids(db, user_id)

    async def introduce_myself(self, schema) -> FavoriteResponse:
        return FavoriteResponse(id=schema.id, name=schema.name)
