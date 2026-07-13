from dataclasses import dataclass


@dataclass(frozen=True)
class DiscordQuery:
    id: int
    name: str


@dataclass(frozen=True)
class DiscordMessageCommand:
    channel_id: str
    username: str
    content: str


@dataclass(frozen=True)
class DiscordResponse:
    id: int
    name: str


@dataclass(frozen=True)
class DiscordMessageResult:
    channel_id: str
    bot_reply: str
