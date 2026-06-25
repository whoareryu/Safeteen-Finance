from pydantic import BaseModel, Field


class GraphNodeSchema(BaseModel):
    node_id: str
    node_type: str
    links: list[str]


class GraphSummaryResponseSchema(BaseModel):
    nodes: list[GraphNodeSchema]
    hub_count: int
    spoke_count: int
    edge_count: int
