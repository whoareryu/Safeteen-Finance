from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ChatCommand:
    messages: list[ChatMessage]


@dataclass(frozen=True)
class ChatResult:
    text: str
    model: str
