from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from user.adapter.outbound.orm.favorite_orm import Favorite
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.pg.restaurant_orm_loads import RESTAURANT_CARD_LOADS
from user.app.ports.output.favorite_repository import FavoriteRepository


class FavoritePgRepository(FavoriteRepository):
    def resolve_restaurant_id(self, db: Session, store_id: int) -> int | None:
        row = db.get(Restaurant, store_id)
        return row.id if row is not None else None

    def toggle(self, db: Session, *, user_id: int, restaurant_id: int) -> bool:
        existing = db.execute(
            select(Favorite.id)
            .where(Favorite.user_id == user_id, Favorite.restaurant_id == restaurant_id)
            .limit(1)
        ).scalar_one_or_none()

        if existing is not None:
            db.execute(
                delete(Favorite).where(
                    Favorite.user_id == user_id,
                    Favorite.restaurant_id == restaurant_id,
                )
            )
            db.commit()
            return False

        db.add(Favorite(user_id=user_id, restaurant_id=restaurant_id))
        db.commit()
        return True

    def list_favorites(self, db: Session, user_id: int) -> list[Favorite]:
        return list(
            db.scalars(
                select(Favorite)
                .where(Favorite.user_id == user_id)
                .options(
                    joinedload(Favorite.restaurant).options(*RESTAURANT_CARD_LOADS)
                )
                .order_by(Favorite.created_at.desc())
            )
            .unique()
            .all()
        )

    def is_favorited(
        self, db: Session, *, user_id: int, restaurant_id: int
    ) -> bool:
        hit = db.execute(
            select(Favorite.id)
            .where(Favorite.user_id == user_id, Favorite.restaurant_id == restaurant_id)
            .limit(1)
        ).scalar_one_or_none()
        return hit is not None

    def list_restaurant_ids(self, db: Session, user_id: int) -> list[int]:
        return list(
            db.scalars(
                select(Favorite.restaurant_id).where(Favorite.user_id == user_id)
            ).all()
        )
