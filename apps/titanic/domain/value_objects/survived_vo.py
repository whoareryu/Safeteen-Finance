from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Survived:
    value: Optional[bool]

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "Survived":
        if not raw or not str(raw).strip():
            return cls(value=None)
        stripped = str(raw).strip()
        if stripped == "1":
            return cls(value=True)
        if stripped == "0":
            return cls(value=False)
        raise ValueError(f"Survived 파싱 실패: {raw!r}")

    @property
    def is_unknown(self) -> bool:
        return self.value is None

    def __str__(self) -> str:
        if self.value is None:
            return "미상"
        return "생존" if self.value else "사망"
