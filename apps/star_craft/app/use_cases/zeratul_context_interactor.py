from __future__ import annotations

from star_craft.app.dtos.zeratul_context_dto import ContextQuery, ContextRouteResponse
from star_craft.app.ports.input.zeratul_context_use_case import ZeratulContextUseCase
from star_craft.app.ports.output.zeratul_context_port import ZeratulContextPort

_KEYWORD_MAP: dict[str, str] = {
    "titanic": "titanic",
    "생존": "titanic",
    "맛집": "restaurant",
    "restaurant": "restaurant",
    "음식": "restaurant",
    "날씨": "restaurant",
    "실리콘밸리": "silicon_valley",
    "silicon": "silicon_valley",
    "즐겨찾기": "user",
    "user": "user",
}


class ZeratulContextInteractor(ZeratulContextUseCase):
    """Zeratul — 다크 아콘. 의도(intent) 분석으로 라우팅 스포크를 결정한다."""

    def __init__(self, repository: ZeratulContextPort) -> None:
        self._repository = repository

    async def route_context(self, query: ContextQuery) -> ContextRouteResponse:
        combined = f"{query.intent} {query.payload}".lower()
        for keyword, spoke in _KEYWORD_MAP.items():
            if keyword in combined:
                return ContextRouteResponse(
                    target_spoke=spoke,
                    confidence=0.85,
                    reason=f"키워드 '{keyword}' 감지",
                )
        return ContextRouteResponse(
            target_spoke="unknown",
            confidence=0.0,
            reason="매칭 스포크 없음",
        )
