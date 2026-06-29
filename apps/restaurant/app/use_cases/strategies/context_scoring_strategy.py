"""맥락 기반 추천 점수 전략 (규칙기반, 광고 비개입 — 기획서 4-1)."""

from __future__ import annotations

import random

from restaurant.app.dtos.personalized_recommendation_dto import PersonalizedQuery
from restaurant.app.use_cases.strategies.recommendation_scoring_strategy import (
    RecommendationScoringStrategy,
)

# 시간대별 가중 (slug → 보너스)
_TIME_SLOT_BONUS: dict[str, dict[str, float]] = {
    "morning": {"cafe-dessert": 2.0, "bunsik": 1.0, "hansik": 0.5},
    "lunch": {"hansik": 1.5, "jungsik": 1.2, "bunsik": 1.2, "ilsik": 1.0, "asian": 1.0},
    "dinner": {"bar": 1.8, "ilsik": 1.2, "yangsik": 1.2, "hansik": 1.0},
}
# 비/눈 → 국물 장르 보너스
_WET_BONUS: dict[str, float] = {"hansik": 1.2, "bunsik": 1.0, "jungsik": 0.8}
_WET_KEYWORDS = ("비", "눈", "rain", "Rain", "snow", "Snow", "drizzle")


class ContextScoringStrategy(RecommendationScoringStrategy):
    def score(self, candidate: dict, query: PersonalizedQuery) -> float:
        slug = candidate.get("slug", "")
        label = candidate.get("genre", "")
        # 다양성 지터 — 같은 맥락이라도 매번 다른 추천
        score = random.uniform(0.0, 0.5)

        # 취향 순위: 앞 순위일수록 큰 가중
        for i, g in enumerate(query.preference.genre_ranking):
            if g in (slug, label):
                score += max(0.0, 3.0 - i * 0.5)
                break

        score += _TIME_SLOT_BONUS.get(query.time_slot, {}).get(slug, 0.0)

        weather = query.weather or ""
        if any(k in weather for k in _WET_KEYWORDS):
            score += _WET_BONUS.get(slug, 0.0)

        return score
