from fastapi import APIRouter, Depends

from ontology.adapter.inbound.api.schemas.ontology_schema import GraphQueryRequest, GraphQueryResponse
from ontology.app.dtos.sommelier_dto import GraphQueryDto
from ontology.app.ports.input.sommelier_graph_use_case import SommelierUseCase
from ontology.dependencies.sommelier_graph_provider import get_sommelier_use_case

sommelier_graph_router = APIRouter(prefix="/graph", tags=["ontology-graph"])


@sommelier_graph_router.post("/query", response_model=GraphQueryResponse)
async def query_graph(
    body: GraphQueryRequest,
    use_case: SommelierUseCase = Depends(get_sommelier_use_case),
) -> GraphQueryResponse:
    result = await use_case.query(GraphQueryDto(cypher=body.cypher, params=body.params))
    return GraphQueryResponse(records=result.records)
