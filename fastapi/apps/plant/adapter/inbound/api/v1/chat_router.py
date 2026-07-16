from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ontology.app.ports.input.semantic_routing_use_case import SemanticRoutingUseCase
from ontology.dependencies.semantic_routing_provider import get_semantic_routing_use_case

from plant.adapter.inbound.api.schemas.chat_schema import ChatRequest, ChatResponse
from plant.adapter.inbound.mappers.chat_mapper import to_command, to_response

chat_router = APIRouter(tags=["plant-chat"])


@chat_router.post("/chat", summary="Qwen 라우팅 식물 채팅 (DB 있으면 RAG, 없으면 Gemini)")
async def chat(
    request: ChatRequest,
    use_case: SemanticRoutingUseCase = Depends(get_semantic_routing_use_case),
) -> ChatResponse:
    if not request.messages:
        raise HTTPException(status_code=422, detail="messages는 최소 1개 이상이어야 합니다.")
    try:
        result = await use_case.route(to_command(request))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"식물 채팅 처리 실패: {e!s}") from e
    return to_response(result)
