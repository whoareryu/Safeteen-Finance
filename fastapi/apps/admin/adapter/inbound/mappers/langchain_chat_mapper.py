from __future__ import annotations

from admin.adapter.inbound.api.schemas.langchain_chat_schema import ChatResponseSchema
from admin.app.dtos.langchain_chat_dto import ChatResult


def to_response(result: ChatResult) -> ChatResponseSchema:
    return ChatResponseSchema(reply=result.reply)
