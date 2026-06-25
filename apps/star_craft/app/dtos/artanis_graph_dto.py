from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GraphNodeQuery:
    node_id: str | None = None


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: str  # "hub" | "spoke"
    links: tuple[str, ...]


@dataclass(frozen=True)
class GraphSummaryResponse:
    nodes: tuple[GraphNode, ...]
    hub_count: int
    spoke_count: int
    edge_count: int
