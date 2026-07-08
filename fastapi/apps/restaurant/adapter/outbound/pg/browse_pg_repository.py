"""Browse / search SQL — ORM·DB 접근은 어댑터 레이어에서만."""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.biz_classification_orm import BizClassification
from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.orm.sigungu_district_orm import SigunguDistrict
from restaurant.app.dtos.restaurant_browse_dto import RestaurantBrowseRow
from restaurant.app.ports.output.restaurant_browse_repository import IRestaurantBrowseRepository


_BROWSE_COLUMNS = (
    Restaurant.id,
    Restaurant.name,
    Restaurant.store_name,
    Restaurant.branch_name,
    FoodCategory.slug,
    FoodCategory.label,
    BizClassification.biz_mid_name,
    BizClassification.biz_minor_name,
    BizClassification.ksic_name,
    Restaurant.biz_number,
    SigunguDistrict.district_label,
    SigunguDistrict.sigungu_name,
    Restaurant.latitude,
    Restaurant.longitude,
    Restaurant.road_address,
    Restaurant.parcel_address,
    Restaurant.image_url,
)

_TEXT_SEARCH_COLUMNS = (
    Restaurant.name,
    Restaurant.store_name,
    Restaurant.branch_name,
    BizClassification.biz_mid_name,
    BizClassification.biz_minor_name,
    BizClassification.ksic_name,
    SigunguDistrict.district_label,
    SigunguDistrict.sigungu_name,
    Restaurant.road_address,
    Restaurant.parcel_address,
)


def _row_from_tuple(t: tuple) -> RestaurantBrowseRow:
    return RestaurantBrowseRow(
        id=int(t[0]),
        name=str(t[1] or ""),
        store_name=str(t[2] or ""),
        branch_name=str(t[3] or ""),
        category_slug=str(t[4] or "hansik"),
        category_label=str(t[5] or ""),
        biz_mid_name=str(t[6] or ""),
        biz_minor_name=str(t[7] or ""),
        ksic_name=str(t[8] or ""),
        biz_number=str(t[9] or ""),
        district=str(t[10] or ""),
        sigungu_name=str(t[11] or ""),
        latitude=t[12],
        longitude=t[13],
        road_address=str(t[14] or ""),
        parcel_address=str(t[15] or ""),
        image_url=str(t[16] or ""),
    )


def _base_select():
    return (
        select(*_BROWSE_COLUMNS)
        .join(FoodCategory, Restaurant.category_id == FoodCategory.id)
        .join(SigunguDistrict, Restaurant.sigungu_id == SigunguDistrict.id)
        .join(BizClassification, Restaurant.biz_classification_id == BizClassification.id)
    )


class BrowsePgRepository(IRestaurantBrowseRepository):
    def count_restaurants(
        self, db: Session, *, category_slug: str | None = None
    ) -> int:
        stmt = select(func.count()).select_from(Restaurant).join(
            FoodCategory, Restaurant.category_id == FoodCategory.id
        )
        if category_slug:
            stmt = stmt.where(FoodCategory.slug == category_slug)
        return int(db.execute(stmt).scalar_one() or 0)

    def bounded_slice(
        self,
        db: Session,
        *,
        limit_rows: int = 10_000,
        rotation_salt: int = 0,
        day_ord: int | None = None,
        total_row_count: int | None = None,
        category_slug: str | None = None,
    ) -> list[RestaurantBrowseRow]:
        do = day_ord if day_ord is not None else date.today().toordinal()
        cnt = (
            int(total_row_count)
            if total_row_count is not None
            else self.count_restaurants(db, category_slug=category_slug)
        )
        if cnt == 0:
            return []
        n = min(limit_rows, cnt)
        span = cnt - n
        off = ((do * 79_691 + rotation_salt * 3_961) % (span + 1)) if span > 0 else 0
        stmt = _base_select()
        if category_slug:
            stmt = stmt.where(FoodCategory.slug == category_slug)
        stmt = stmt.order_by(Restaurant.id).offset(off).limit(n)
        return [_row_from_tuple(t) for t in db.execute(stmt).all()]

    def fetch_text_search_candidates(
        self,
        db: Session,
        *,
        patterns: list[str],
        limit: int = 1_600,
    ) -> list[RestaurantBrowseRow]:
        uniq: list[str] = []
        for p in patterns:
            if p and p not in uniq:
                uniq.append(p)
            if len(uniq) >= 14:
                break
        if not uniq:
            return self.bounded_slice(db, limit_rows=min(6_000, limit * 4))
        parts = [or_(*[col.ilike(p) for col in _TEXT_SEARCH_COLUMNS]) for p in uniq]
        cond = or_(*parts) if len(parts) > 1 else parts[0]
        stmt = _base_select().where(cond).limit(limit)
        rows = [_row_from_tuple(t) for t in db.execute(stmt).all()]
        if not rows:
            return self.bounded_slice(db, limit_rows=min(8_000, limit * 5))
        return rows

    def display_name_by_id(self, db: Session, store_id: int) -> str | None:
        r = db.get(Restaurant, store_id)
        if r is None:
            return None
        return r.display_name()
