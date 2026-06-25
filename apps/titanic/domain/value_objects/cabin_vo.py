from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Cabin:
    value: str

    @property
    def is_unknown(self) -> bool:
        return not self.value.strip()

    @property
    def deck(self) -> str | None:
        return self.value[0].upper() if self.value.strip() else None

    def __str__(self) -> str:
        return self.value if self.value else "미상"
