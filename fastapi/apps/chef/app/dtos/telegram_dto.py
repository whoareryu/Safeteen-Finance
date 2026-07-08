from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramQuery:
    id: int
    name: str


@dataclass(frozen=True)
class TelegramResponse:
    id: int
    name: str
