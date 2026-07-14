from __future__ import annotations

from pydantic import BaseModel


class ChatMessageSchema(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessageSchema]
    model: str | None = None


class ChatResponse(BaseModel):
    text: str
    model: str
