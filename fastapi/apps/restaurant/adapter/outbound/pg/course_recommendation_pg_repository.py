from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.orm.sigungu_district_orm import SigunguDistrict
from restaurant.app.ports.output.course_recommendation_repository import (
    CourseRecommendationRepository,
)


class CourseRecommendationPgRepository(CourseRecommendationRepository):
    def find_one_by_district_and_slot(
        self, db: Session, *, district: str, category_slug: str
    ) -> dict | None:
        stmt = (
            select(Restaurant.id, Restaurant.name)
            .join(FoodCategory, Restaurant.category_id == FoodCategory.id)
            .join(SigunguDistrict, Restaurant.sigungu_id == SigunguDistrict.id)
            .where(
                FoodCategory.slug == category_slug,
                SigunguDistrict.district_label.like(f"%{district}%"),
                Restaurant.latitude.is_not(None),
            )
            .order_by(func.random())
            .limit(1)
        )
        row = db.execute(stmt).first()
        return {"id": row.id, "name": row.name} if row else None
