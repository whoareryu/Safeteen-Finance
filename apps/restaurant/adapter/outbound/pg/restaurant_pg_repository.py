"""``restaurants`` 테이블 — Bulk Insert·Builder 기반 조회."""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.orm.sigungu_district_orm import SigunguDistrict
from restaurant.adapter.outbound.pg.restaurant_orm_loads import RESTAURANT_DETAIL_LOADS
from restaurant.adapter.outbound.pg.base_pg_repository import AbstractRepository
from restaurant.app.ports.output.restaurant_repository import IRestaurantRepository
from restaurant.adapter.outbound.pg.restaurant_query_builder import RestaurantQueryBuilder


class RestaurantRepository(AbstractRepository[Restaurant], IRestaurantRepository):
    """``IRestaurantRepository`` 구현 — DB 접근 은닉."""

    def get_by_id(self, db: Session, restaurant_id: int) -> Restaurant | None:
        return db.scalars(
            select(Restaurant)
            .where(Restaurant.id == restaurant_id)
            .options(*RESTAURANT_DETAIL_LOADS)
        ).first()

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
        builder = RestaurantQueryBuilder().category(category_slug).order_for_browse()
        if district:
            builder.district_contains(district)
        return builder.paginate(offset, limit).scalars(db)

    def list_within_budget(
        self,
        db: Session,
        *,
        max_avg_price: int,
        category_slug: str | None,
        offset: int,
        limit: int,
    ) -> list[Restaurant]:
        builder = (
            RestaurantQueryBuilder()
            .max_avg_price(max_avg_price)
            .order_for_browse()
        )
        if category_slug:
            builder.category(category_slug)
        return builder.paginate(offset, limit).scalars(db)

    def count_by_category(
        self, db: Session, *, category_slug: str, district: str | None = None
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(Restaurant)
            .join(FoodCategory, Restaurant.category_id == FoodCategory.id)
            .where(FoodCategory.slug == category_slug)
        )
        if district:
            stmt = stmt.join(
                SigunguDistrict, Restaurant.sigungu_id == SigunguDistrict.id
            ).where(SigunguDistrict.district_label.ilike(f"%{district}%"))
        return int(db.execute(stmt).scalar_one() or 0)
