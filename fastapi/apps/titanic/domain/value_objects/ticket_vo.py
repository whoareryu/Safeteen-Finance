from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TicketNumber:
    value: str

    def __post_init__(self) -> None:
        if len(self.value) > 128:
            raise ValueError("TicketNumber는 최대 128자입니다.")

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "TicketNumber":
        stripped = raw.strip() if raw else ""
        if len(stripped) > 128:
            raise ValueError("TicketNumber는 최대 128자입니다.")
        return cls(value=stripped)

    @property
    def is_known(self) -> bool:
        return bool(self.value and self.value.strip())

    @property
    def prefix(self) -> Optional[str]:
        parts = self.value.split()
        return parts[0] if len(parts) > 1 else None

    def __str__(self) -> str:
        return self.value or "미상"
