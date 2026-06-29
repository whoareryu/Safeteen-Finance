from __future__ import annotations

from sqlalchemy.orm import Session

from restaurant.app.dtos.course_recommendation_dto import (
    CourseQuery,
    CourseStop,
    CourseView,
)
from restaurant.app.ports.input.course_recommendation_use_case import (
    CourseRecommendationUseCase,
)
from restaurant.app.ports.output.course_recommendation_repository import (
    CourseRecommendationRepository,
)

# 하루 코스 순서: (표시 라벨, 카테고리 slug) — 기획서 3-4
_COURSE_SLOTS: list[tuple[str, str]] = [
    ("브런치", "yangsik"),
    ("점심", "hansik"),
    ("카페", "cafe-dessert"),
    ("저녁", "ilsik"),
    ("술집", "bar"),
]


class CourseRecommendationInteractor(CourseRecommendationUseCase):
    def __init__(self, repository: CourseRecommendationRepository) -> None:
        self._repository = repository

    def recommend(self, db: Session, query: CourseQuery) -> CourseView:
        stops: list[CourseStop] = []
        for label, slug in _COURSE_SLOTS:
            row = self._repository.find_one_by_district_and_slot(
                db, district=query.district, category_slug=slug
            )
            if row is not None:
                stops.append(
                    CourseStop(slot=label, restaurant_id=row["id"], name=row["name"])
                )
        return CourseView(district=query.district, stops=stops)
