from __future__ import annotations
from dataclasses import dataclass


@dataclass
class DiscordEntity:
    id: int
    channel_id: str
    username: str
    content: str
    bot_reply: str = ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DiscordEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def introduce_myself(self) -> str:
        return f"DiscordAgent(channel_id={self.channel_id}, user={self.username})"
