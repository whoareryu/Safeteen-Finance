"""Restaurant 조회 조건 Builder — 복합 인덱스와 1:1 대응."""

from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.orm.restaurant_price_orm import RestaurantPrice
from restaurant.adapter.outbound.orm.sigungu_district_orm import SigunguDistrict
from restaurant.adapter.outbound.pg.restaurant_orm_loads import RESTAURANT_CARD_LOADS


class RestaurantQueryBuilder:
    """``restaurants`` 쿼리를 단계적으로 조립 (GOF Builder)."""

    def __init__(self) -> None:
        self._stmt: Select = select(Restaurant).options(*RESTAURANT_CARD_LOADS)
        self._category_slug: str | None = None
        self._district: str | None = None
        self._max_avg_price: int | None = None
        self._joined_category = False
        self._joined_price = False
        self._joined_sigungu = False

    def _ensure_category_join(self) -> None:
        if not self._joined_category:
            self._stmt = self._stmt.join(
                FoodCategory, Restaurant.category_id == FoodCategory.id
            )
            self._joined_category = True

    def _ensure_price_join(self) -> None:
        if not self._joined_price:
            self._stmt = self._stmt.outerjoin(
                RestaurantPrice, RestaurantPrice.restaurant_id == Restaurant.id
            )
            self._joined_price = True

    def category(self, slug: str) -> RestaurantQueryBuilder:
        self._category_slug = slug
        self._ensure_category_join()
        self._stmt = self._stmt.where(FoodCategory.slug == slug)
        return self

    def _ensure_sigungu_join(self) -> None:
        if not self._joined_sigungu:
            self._stmt = self._stmt.join(
                SigunguDistrict, Restaurant.sigungu_id == SigunguDistrict.id
            )
            self._joined_sigungu = True

    def district_contains(self, district: str) -> RestaurantQueryBuilder:
        self._district = district
        self._ensure_sigungu_join()
        self._stmt = self._stmt.where(
            SigunguDistrict.district_label.ilike(f"%{district}%")
        )
        return self

    def max_avg_price(self, cap: int) -> RestaurantQueryBuilder:
        self._max_avg_price = cap
        self._ensure_price_join()
        self._stmt = (
            self._stmt.where(RestaurantPrice.avg_price.is_not(None))
            .where(RestaurantPrice.avg_price <= cap)
        )
        return self

    def order_for_browse(self) -> RestaurantQueryBuilder:
        if self._max_avg_price is not None:
            self._ensure_category_join()
            self._ensure_price_join()
            self._stmt = self._stmt.order_by(
                FoodCategory.slug, RestaurantPrice.avg_price, Restaurant.id
            )
        elif self._category_slug:
            self._stmt = self._stmt.order_by(Restaurant.id)
        else:
            self._stmt = self._stmt.order_by(Restaurant.id)
        return self

    def paginate(self, offset: int, limit: int) -> RestaurantQueryBuilder:
        self._stmt = self._stmt.offset(offset).limit(limit)
        return self

    def build(self) -> Select:
        return self._stmt

    def scalars(self, db: Session) -> list[Restaurant]:
        return list(db.scalars(self._stmt).unique().all())
