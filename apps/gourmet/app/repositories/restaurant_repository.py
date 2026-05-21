"""``restaurants`` 테이블 — Bulk Insert·복합 인덱스 기반 조회."""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from apps.gourmet.app.models.restaurant import Restaurant
from apps.gourmet.app.repositories.interfaces import IRestaurantRepository


class RestaurantRepository:
    """``IRestaurantRepository`` 구현."""

    def get_by_id(self, db: Session, restaurant_id: int) -> Restaurant | None:
        return db.get(Restaurant, restaurant_id)

    def bulk_insert(
        self, db: Session, rows: list[Restaurant], *, commit: bool = True
    ) -> int:
        if not rows:
            return 0
        db.add_all(rows)
        if commit:
            db.commit()
        return len(rows)

    def delete_all(self, db: Session) -> int:
        count = db.execute(delete(Restaurant)).rowcount or 0
        db.commit()
        return count

    def list_by_category(
        self,
        db: Session,
        *,
        category_slug: str,
        offset: int,
        limit: int,
        district: str | None = None,
    ) -> list[Restaurant]:
        stmt = (
            select(Restaurant)
            .where(Restaurant.category_slug == category_slug)
            .order_by(Restaurant.id)
            .offset(offset)
            .limit(limit)
        )
        if district:
            stmt = stmt.where(Restaurant.district.ilike(f"%{district}%"))
        return list(db.scalars(stmt).all())

    def list_within_budget(
        self,
        db: Session,
        *,
        max_avg_price: int,
        category_slug: str | None,
        offset: int,
        limit: int,
    ) -> list[Restaurant]:
        stmt = (
            select(Restaurant)
            .where(Restaurant.avg_price.is_not(None))
            .where(Restaurant.avg_price <= max_avg_price)
            .order_by(Restaurant.category_slug, Restaurant.avg_price, Restaurant.id)
            .offset(offset)
            .limit(limit)
        )
        if category_slug:
            stmt = stmt.where(Restaurant.category_slug == category_slug)
        return list(db.scalars(stmt).all())

    def count_by_category(
        self, db: Session, *, category_slug: str, district: str | None = None
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(Restaurant)
            .where(Restaurant.category_slug == category_slug)
        )
        if district:
            stmt = stmt.where(Restaurant.district.ilike(f"%{district}%"))
        return int(db.execute(stmt).scalar_one() or 0)
