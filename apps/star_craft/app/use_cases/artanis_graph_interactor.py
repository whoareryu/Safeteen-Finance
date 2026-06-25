from __future__ import annotations

from star_craft.app.dtos.artanis_graph_dto import GraphNode, GraphNodeQuery, GraphSummaryResponse
from star_craft.app.ports.input.artanis_graph_use_case import ArtanisGraphUseCase
from star_craft.app.ports.output.artanis_graph_port import ArtanisGraphPort


class ArtanisGraphInteractor(ArtanisGraphUseCase):
    """Artanis — 프로토스 아키텍트. 온톨로지 지식 그래프 인덱스를 관리한다."""

    def __init__(self, repository: ArtanisGraphPort) -> None:
        self._repository = repository

    async def get_graph_summary(self, query: GraphNodeQuery) -> GraphSummaryResponse:
        return await self._repository.fetch_graph_summary(query)
