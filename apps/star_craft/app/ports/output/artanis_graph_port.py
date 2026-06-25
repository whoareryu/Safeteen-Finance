from __future__ import annotations

from abc import ABC, abstractmethod

from star_craft.app.dtos.artanis_graph_dto import GraphNodeQuery, GraphSummaryResponse


class ArtanisGraphPort(ABC):

    @abstractmethod
    async def fetch_graph_summary(self, query: GraphNodeQuery) -> GraphSummaryResponse:
        pass
