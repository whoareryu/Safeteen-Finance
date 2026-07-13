from __future__ import annotations

import asyncio

from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator
from restaurant.app.dtos.personalized_recommendation_dto import PersonalizedQuery
from restaurant.app.ports.output.reason_generator_port import ReasonGeneratorPort

_MODEL = "exaone3.5:2.4b"
_SLOT_LABEL = {"morning": "아침", "lunch": "점심", "dinner": "저녁"}
_DINING_LABEL = {"dine_in": "매장에서 먹기", "pickup": "포장", "delivery": "배달"}
_TIMEOUT_SECONDS = 8.0


class OllamaReasonGenerator(ReasonGeneratorPort):
    """추천 이유 생성 전용 로컬 모델(exaone3.5:2.4b) — chat 기능의 keymaker(7.8b)와는
    별도 인스턴스로, 모델 하나당 하나의 일만 맡는다.

    Ollama가 응답하지 않거나 오류가 나면 fallback(TemplateReasonGenerator)으로 위임해
    추천 자체는 항상 성공하도록 한다.
    """

    def __init__(self, fallback: ReasonGeneratorPort) -> None:
        self._fallback = fallback
        self._orchestrator = T1MidFakerOrchestrator(model=_MODEL)

    async def generate(self, candidate: dict, query: PersonalizedQuery) -> str:
        prompt = self._build_prompt(candidate, query)
        try:
            text = await asyncio.wait_for(
                self._orchestrator.generate(prompt),
                timeout=_TIMEOUT_SECONDS,
            )
            text = text.strip().strip('"')
            if text:
                return text
        except Exception:
            pass
        return await self._fallback.generate(candidate, query)

    def _build_prompt(self, candidate: dict, query: PersonalizedQuery) -> str:
        slot = _SLOT_LABEL.get(query.time_slot, "오늘")
        dining = _DINING_LABEL.get(query.dining_mode or "", "")
        lines = [
            "당신은 서울 맛집 앱 GourmetMate의 추천 문구 작성 도우미입니다.",
            "아래 식당을 오늘의 추천으로 보여줄 때 붙일 이유를 한 문장으로 자연스럽게 한국어로 써주세요.",
            "설명이나 따옴표 없이 문장 하나만 출력하세요.",
            f"- 식당 이름: {candidate.get('name', '')}",
            f"- 음식 종류: {candidate.get('genre', '')}",
            f"- 시간대: {slot}",
        ]
        if dining:
            lines.append(f"- 이용 방식: {dining}")
        if query.weather:
            lines.append(f"- 오늘 날씨: {query.weather}")
        if query.preference.genre_ranking:
            lines.append(
                f"- 사용자가 좋아하는 음식 순위: {', '.join(query.preference.genre_ranking)}"
            )
        return "\n".join(lines)
