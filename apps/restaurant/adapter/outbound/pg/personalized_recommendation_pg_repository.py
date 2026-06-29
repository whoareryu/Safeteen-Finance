from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.app.ports.output.personalized_recommendation_repository import (
    PersonalizedRecommendationRepository,
)


class PersonalizedRecommendationPgRepository(PersonalizedRecommendationRepository):
    """제외 식당을 뺀 무작위 후보 풀 조회 (전략이 풀 안에서 점수화)."""

    def candidate_restaurants(
        self, db: Session, *, excluded_ids: list[int], limit: int
    ) -> list[dict]:
        stmt = (
            select(
                Restaurant.id,
                Restaurant.name,
                Restaurant.road_address,
                Restaurant.latitude,
                Restaurant.longitude,
                FoodCategory.slug,
                FoodCategory.label,
            )
            .join(FoodCategory, Restaurant.category_id == FoodCategory.id)
            .where(Restaurant.latitude.is_not(None))
        )
        if excluded_ids:
            stmt = stmt.where(Restaurant.id.not_in(excluded_ids))
        stmt = stmt.order_by(func.random()).limit(limit)

        return [
            {
                "id": row.id,
                "name": row.name,
                "road_address": row.road_address or "",
                "latitude": row.latitude,
                "longitude": row.longitude,
                "slug": row.slug,
                "genre": row.label,
            }
            for row in db.execute(stmt).all()
        ]
