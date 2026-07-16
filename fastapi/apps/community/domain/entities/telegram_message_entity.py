from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TelegramMessageEntity:
    id: int | None
    text: str
    sent_at: datetime
