"""즐겨찾기 — ``restaurants.id`` 단일 카탈로그."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from apps.auth.user_model import User
from apps.gourmet.app.models.favorite import Favorite
from apps.gourmet.app.models.restaurant import Restaurant
from apps.gourmet.app.repositories.restaurant_orm_loads import RESTAURANT_CARD_LOADS


def resolve_restaurant_id(db: Session, store_id: int) -> int | None:
    """UI ``store_id`` → ``restaurants.id``."""
    row = db.get(Restaurant, store_id)
    return row.id if row is not None else None


def find_store_id_for_restaurant(db: Session, restaurant_id: int) -> int:
    """카드·링크용 id — ``restaurants.id`` 와 동일."""
    row = db.get(Restaurant, restaurant_id)
    return row.id if row is not None else restaurant_id


class FavoriteService:
    def toggle(self, db: Session, user: User, store_id: int) -> tuple[bool, str]:
        rid = resolve_restaurant_id(db, store_id)
        if rid is None:
            raise ValueError("매장을 찾을 수 없습니다.")

        existing = db.execute(
            select(Favorite.id)
            .where(Favorite.user_id == user.id, Favorite.restaurant_id == rid)
            .limit(1)
        ).scalar_one_or_none()

        if existing is not None:
            db.execute(
                delete(Favorite).where(
                    Favorite.user_id == user.id, Favorite.restaurant_id == rid
                )
            )
            db.commit()
            return False, "즐겨찾기에서 제거했습니다."

        db.add(Favorite(user_id=user.id, restaurant_id=rid))
        db.commit()
        return True, "즐겨찾기에 추가했습니다."

    def list_cards(self, db: Session, user_id: int) -> list[dict]:
        favs = db.scalars(
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .options(
                joinedload(Favorite.restaurant).options(*RESTAURANT_CARD_LOADS)
            )
            .order_by(Favorite.created_at.desc())
        ).unique().all()
        out: list[dict] = []
        for fav in favs:
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

    def favorited_store_ids(
        self, db: Session, user_id: int, store_ids: list[int]
    ) -> list[int]:
        favorited: list[int] = []
        for sid in store_ids:
            rid = resolve_restaurant_id(db, sid)
            if rid is None:
                continue
            hit = db.execute(
                select(Favorite.id)
                .where(Favorite.user_id == user_id, Favorite.restaurant_id == rid)
                .limit(1)
            ).scalar_one_or_none()
            if hit is not None:
                favorited.append(sid)
        return favorited

    def all_favorited_store_ids_for_user(self, db: Session, user_id: int) -> list[int]:
        rids = list(
            db.scalars(
                select(Favorite.restaurant_id).where(Favorite.user_id == user_id)
            ).all()
        )
        return list(rids)
