"""``food_categories`` 마스터 조회."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from gourmet.adapter.outbound.orm.food_category import FoodCategory
from gourmet.adapter.outbound.pg.food_category_repository import FoodCategoryRepository


def list_food_categories(db: Session) -> list[dict]:
    FoodCategoryRepository().ensure_seeded(db)
    rows = db.scalars(select(FoodCategory).order_by(FoodCategory.id)).all()
    return [{"id": c.id, "slug": c.slug, "label": c.label} for c in rows]
