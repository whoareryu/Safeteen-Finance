from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReceiverEntity:
    id: int
    sender: str
    recipient: str
    subject: str
    preview: str
    received_at: datetime

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ReceiverEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
