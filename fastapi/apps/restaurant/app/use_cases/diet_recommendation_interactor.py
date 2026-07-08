from __future__ import annotations

from sqlalchemy.orm import Session

from restaurant.app.dtos.diet_recommendation_dto import DietQuery, DietView
from restaurant.app.ports.input.diet_recommendation_use_case import (
    DietRecommendationUseCase,
)
from restaurant.app.ports.output.diet_recommendation_repository import (
    DietRecommendationRepository,
)

# 식단 유형 → 근사 카테고리 slug (CSV에 영양정보 없음 → 장르 휴리스틱, 기획서 3-4)
_DIET_SLUGS: dict[str, list[str]] = {
    "high_protein": ["hansik", "ilsik", "yangsik"],  # 고단백 (고기·생선·스테이크)
    "low_carb": ["ilsik", "yangsik", "asian"],  # 저탄수 (밥·면 비중 낮은 쪽 근사)
}
_DEFAULT_SLUGS = ["hansik", "ilsik", "yangsik"]
_LIMIT = 20


class DietRecommendationInteractor(DietRecommendationUseCase):
    def __init__(self, repository: DietRecommendationRepository) -> None:
        self._repository = repository

    def recommend(self, db: Session, query: DietQuery) -> DietView:
        slugs = _DIET_SLUGS.get(query.diet_type, _DEFAULT_SLUGS)
        rows = self._repository.find_by_slugs(
            db, slugs=slugs, district=query.district, limit=_LIMIT
        )
        return DietView(diet_type=query.diet_type, restaurants=rows)
