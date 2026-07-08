from __future__ import annotations
from dataclasses import dataclass


@dataclass
class TelegramEntity:
    id: int
    chat_id: str
    username: str
    text: str
    bot_reply: str = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TelegramEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def introduce_myself(self) -> str:
        return f"TelegramAgent(chat_id={self.chat_id}, user={self.username})"
