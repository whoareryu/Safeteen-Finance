from __future__ import annotations

from pydantic import BaseModel


class ChatRequestSchema(BaseModel):
    message: str


class ChatResponseSchema(BaseModel):
    reply: str
