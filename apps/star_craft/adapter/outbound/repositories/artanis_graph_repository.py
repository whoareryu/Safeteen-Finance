from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from star_craft.app.dtos.artanis_graph_dto import GraphNode, GraphNodeQuery, GraphSummaryResponse
from star_craft.app.ports.output.artanis_graph_port import ArtanisGraphPort

_STATIC_GRAPH = (
    GraphNode(node_id="star_craft", node_type="hub", links=("titanic", "restaurant", "silicon_valley", "user")),
    GraphNode(node_id="titanic", node_type="spoke", links=("star_craft",)),
    GraphNode(node_id="restaurant", node_type="spoke", links=("star_craft",)),
    GraphNode(node_id="silicon_valley", node_type="spoke", links=("star_craft",)),
    GraphNode(node_id="user", node_type="spoke", links=("star_craft",)),
)


class ArtanisGraphRepository(ArtanisGraphPort):

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def fetch_graph_summary(self, query: GraphNodeQuery) -> GraphSummaryResponse:
        nodes = _STATIC_GRAPH
        hub_count = sum(1 for n in nodes if n.node_type == "hub")
        spoke_count = sum(1 for n in nodes if n.node_type == "spoke")
        edge_count = sum(len(n.links) for n in nodes) // 2
        return GraphSummaryResponse(
            nodes=nodes,
            hub_count=hub_count,
            spoke_count=spoke_count,
            edge_count=edge_count,
        )
