from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Parch:
    value: int

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError(f"Parch는 0 이상이어야 합니다: {self.value}")

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "Parch":
        if not raw or not str(raw).strip():
            return cls(value=0)
        return cls(value=int(raw))

    def __str__(self) -> str:
        return str(self.value)
