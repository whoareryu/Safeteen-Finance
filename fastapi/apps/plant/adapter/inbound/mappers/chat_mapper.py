from __future__ import annotations

from ontology.app.dtos.semantic_routing_dto import SemanticRoutingQueryDto, SemanticRoutingResultDto

from plant.adapter.inbound.api.schemas.chat_schema import ChatRequest, ChatResponse


def to_command(request: ChatRequest) -> SemanticRoutingQueryDto:
    return SemanticRoutingQueryDto(question=request.messages[-1].content)


def to_response(result: SemanticRoutingResultDto) -> ChatResponse:
    return ChatResponse(text=result.answer, model=result.destination)
