from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReceiverCommand:
    sender: str
    recipient: str
    subject: str
    preview: str
    message_id: str


@dataclass
class ReceiverResult:
    id: int
    sender: str
    subject: str
    received_at: str
