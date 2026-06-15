"""``food_categories`` 시드·slug 조회."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.data.category_catalog import CATEGORY_LABEL_BY_SLUG


class FoodCategoryRepository:
    def ensure_seeded(self, db: Session) -> dict[str, int]:
        """표준 장르 slug → id. 없으면 INSERT."""
        existing = {
            row.slug: row.id
            for row in db.scalars(select(FoodCategory)).all()
        }
        for slug, label in CATEGORY_LABEL_BY_SLUG.items():
            if slug not in existing:
                cat = FoodCategory(slug=slug, label=label)
                db.add(cat)
                db.flush()
                existing[slug] = cat.id
        db.commit()
        return existing

    def slug_to_id(self, db: Session) -> dict[str, int]:
        rows = db.scalars(select(FoodCategory)).all()
        if len(rows) < len(CATEGORY_LABEL_BY_SLUG):
            return self.ensure_seeded(db)
        return {r.slug: r.id for r in rows}
