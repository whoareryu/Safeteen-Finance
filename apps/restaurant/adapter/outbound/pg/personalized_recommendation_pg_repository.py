from __future__ import annotations

from sqlalchemy import func, select  # noqa: F401 (func used for power + random)
from sqlalchemy.orm import Session

from restaurant.adapter.outbound.orm.food_category_orm import FoodCategory
from restaurant.adapter.outbound.orm.restaurant_orm import Restaurant
from restaurant.app.ports.output.personalized_recommendation_repository import (
    PersonalizedRecommendationRepository,
)


class PersonalizedRecommendationPgRepository(PersonalizedRecommendationRepository):
    """제외 식당을 뺀 후보 풀 조회 — 위치 제공 시 가까운 순, 미제공 시 무작위."""

    def candidate_restaurants(
        self,
        db: Session,
        *,
        excluded_ids: list[int],
        limit: int,
        lat: float | None = None,
        lng: float | None = None,
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

        if lat is not None and lng is not None:
            # 근사 거리 정렬 (위도 1도 ≈ 111km, 경도 1도 ≈ 88km in Seoul)
            dlat = (Restaurant.latitude - lat) * 111.0
            dlng = (Restaurant.longitude - lng) * 88.0
            dist_sq = func.power(dlat, 2) + func.power(dlng, 2)
            stmt = stmt.order_by(dist_sq).limit(limit)
        else:
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
