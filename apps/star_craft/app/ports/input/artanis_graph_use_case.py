from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.artanis_graph_dto import GraphNodeQuery, GraphSummaryResponse


class ArtanisGraphUseCase(ABC):
    """Inbound 입력 포트 — 지식 그래프 인덱스. 온톨로지 노드 조회·요약."""

    @abstractmethod
    async def get_graph_summary(self, query: GraphNodeQuery) -> GraphSummaryResponse:
        pass
