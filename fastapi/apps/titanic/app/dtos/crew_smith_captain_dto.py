from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class SmithCaptainQuery:

    id: int
    name: str

@dataclass(frozen=True)
class SmithCaptainResponse:

    id: int
    name: str

@dataclass(frozen=True)
class SmithChatCommand:

    message: str

@dataclass(frozen=True)
class SmithChatResponse:

    reply: str
