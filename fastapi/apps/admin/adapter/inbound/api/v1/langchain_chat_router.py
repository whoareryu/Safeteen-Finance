from __future__ import annotations

from fastapi import APIRouter, Depends

from admin.adapter.inbound.mappers.langchain_chat_mapper import to_response
from admin.adapter.inbound.api.schemas.langchain_chat_schema import (
    ChatRequestSchema,
    ChatResponseSchema,
)
from admin.app.dtos.langchain_chat_dto import ChatCommand
from admin.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from admin.dependencies.langchain_chat_provider import get_langchain_chat_use_case

langchain_chat_router = APIRouter(prefix="/langchain", tags=["langchain-chat"])


@langchain_chat_router.post("/chat", summary="LangChain 어시스턴트와 대화")
async def chat(
    body: ChatRequestSchema,
    use_case: LangchainChatUseCase = Depends(get_langchain_chat_use_case),
) -> ChatResponseSchema:
    result = await use_case.chat(ChatCommand(message=body.message))
    return to_response(result)
