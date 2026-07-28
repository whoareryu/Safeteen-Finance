from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatCommand:
    message: str


@dataclass(frozen=True)
class ChatResult:
    reply: str
