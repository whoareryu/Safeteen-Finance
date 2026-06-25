from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.zeratul_context_dto import ContextQuery, ContextRouteResponse


class ZeratulContextUseCase(ABC):
    """Inbound 입력 포트 — 컨텍스트 라우터. 의도(intent)를 분석해 스포크를 결정."""

    @abstractmethod
    async def route_context(self, query: ContextQuery) -> ContextRouteResponse:
        pass
