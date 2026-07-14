from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from plant.adapter.inbound.api.schemas.chat_schema import ChatRequest, ChatResponse
from plant.adapter.inbound.mappers.chat_mapper import to_command, to_response
from plant.app.ports.input.chat_use_case import ChatUseCase
from plant.dependencies.chat_provider import get_chat_use_case

chat_router = APIRouter(tags=["plant-chat"])


@chat_router.post("/chat", summary="RAG 기반 식물 채팅 (ExaOne 3.5:2.4b)")
async def chat(
    request: ChatRequest,
    use_case: ChatUseCase = Depends(get_chat_use_case),
) -> ChatResponse:
    if not request.messages:
        raise HTTPException(status_code=422, detail="messages는 최소 1개 이상이어야 합니다.")
    try:
        result = await use_case.chat(to_command(request))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"식물 채팅 처리 실패: {e!s}") from e
    return to_response(result)
