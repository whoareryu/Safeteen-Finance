from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.adapter.outbound.orm.sigungu_district_orm import SigunguDistrict
from restaurant.app.ports.output.diet_recommendation_repository import (
    DietRecommendationRepository,
)


class DietRecommendationPgRepository(DietRecommendationRepository):
    def find_by_slugs(
        self, db: Session, *, slugs: list[str], district: str | None, limit: int
    ) -> list[dict]:
        if not slugs:
            return []
        stmt = (
            select(
                Restaurant.id,
                Restaurant.name,
                Restaurant.road_address,
                Restaurant.latitude,
                Restaurant.longitude,
                FoodCategory.label,
            )
            .join(FoodCategory, Restaurant.category_id == FoodCategory.id)
            .where(FoodCategory.slug.in_(slugs), Restaurant.latitude.is_not(None))
        )
        if district:
            stmt = stmt.join(
                SigunguDistrict, Restaurant.sigungu_id == SigunguDistrict.id
            ).where(SigunguDistrict.district_label.like(f"%{district}%"))
        stmt = stmt.order_by(func.random()).limit(limit)

        return [
            {
                "id": row.id,
                "name": row.name,
                "genre": row.label,
                "road_address": row.road_address or "",
                "latitude": row.latitude,
                "longitude": row.longitude,
            }
            for row in db.execute(stmt).all()
        ]
