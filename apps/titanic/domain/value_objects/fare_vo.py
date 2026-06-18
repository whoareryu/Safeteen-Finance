from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Fare:
    raw: str

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "Fare":
        return cls(raw=raw or "")

    def as_float(self) -> Optional[float]:
        try:
            return float(self.raw)
        except (ValueError, TypeError):
            return None

    @property
    def is_known(self) -> bool:
        return self.as_float() is not None

    @property
    def is_free(self) -> bool:
        v = self.as_float()
        return v is not None and v == 0.0

    def is_expensive(self, threshold: float = 100.0) -> bool:
        v = self.as_float()
        return v is not None and v >= threshold

    def __str__(self) -> str:
        return self.raw or "미상"
