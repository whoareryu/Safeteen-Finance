from __future__ import annotations
from dataclasses import dataclass


@dataclass
class EmailEntity:
    id: int
    to: str
    subject: str
    body: str

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EmailEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def introduce_myself(self) -> str:
        return f"EmailAgent(id={self.id}, to={self.to})"
