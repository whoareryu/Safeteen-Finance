from __future__ import annotations

from restaurant.app.dtos.personalized_recommendation_dto import PersonalizedQuery
from restaurant.app.ports.output.reason_generator_port import ReasonGeneratorPort

_SLOT_LABEL = {"morning": "아침", "lunch": "점심", "dinner": "저녁"}
_DINING_LABEL = {"dine_in": "매장에서", "pickup": "포장으로", "delivery": "배달로"}


class TemplateReasonGenerator(ReasonGeneratorPort):
    """규칙 기반 템플릿 문구 — LLM 미가용 시 폴백으로 쓰인다."""

    async def generate(self, candidate: dict, query: PersonalizedQuery) -> str:
        genre = candidate.get("genre", "")
        ranking = query.preference.genre_ranking
        slot = _SLOT_LABEL.get(query.time_slot, "오늘")
        dining = _DINING_LABEL.get(query.dining_mode or "", "")
        if genre in ranking or candidate.get("slug", "") in ranking:
            base = f"취향에 맞는 {genre} 한 곳이에요."
        else:
            base = f"{slot}에 어울리는 {genre} 추천이에요."
        if dining:
            return f"{slot}에 {dining} 즐기기 좋은 {genre}이에요."
        return base
