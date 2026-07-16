from fastapi import APIRouter, Depends

from ontology.adapter.inbound.api.schemas.semantic_routing_schema import (
    SemanticRoutingRequest,
    SemanticRoutingResponse,
)
from ontology.app.dtos.semantic_routing_dto import SemanticRoutingQueryDto
from ontology.app.ports.input.semantic_routing_use_case import SemanticRoutingUseCase
from ontology.dependencies.semantic_routing_provider import get_semantic_routing_use_case

semantic_routing_router = APIRouter(tags=["ontology-semantic-routing"])


@semantic_routing_router.post("/semantic-routing", response_model=SemanticRoutingResponse)
async def route_semantically(
    body: SemanticRoutingRequest,
    use_case: SemanticRoutingUseCase = Depends(get_semantic_routing_use_case),
) -> SemanticRoutingResponse:
    result = await use_case.route(SemanticRoutingQueryDto(question=body.question))
    return SemanticRoutingResponse(
        answer=result.answer, destination=result.destination, entities=result.entities
    )
