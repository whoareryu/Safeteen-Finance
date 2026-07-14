from __future__ import annotations

from plant.adapter.inbound.api.schemas.chat_schema import ChatRequest, ChatResponse
from plant.app.dtos.chat_dto import ChatCommand, ChatMessage, ChatResult


def to_command(request: ChatRequest) -> ChatCommand:
    return ChatCommand(
        messages=[ChatMessage(role=m.role, content=m.content) for m in request.messages]
    )


def to_response(result: ChatResult) -> ChatResponse:
    return ChatResponse(text=result.text, model=result.model)
