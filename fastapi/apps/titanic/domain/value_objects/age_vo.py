from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AgeGroup(str, Enum):
    BABY = "Baby"           # 0–2
    CHILD = "Child"         # 3–12
    TEENAGER = "Teenager"   # 13–17
    ADULT = "Adult"         # 18–64
    SENIOR = "Senior"       # 65+
    UNKNOWN = "Unknown"


@dataclass(frozen=True)
class Age:
    value: Optional[float]

    def __post_init__(self) -> None:
        if self.value is not None and (self.value < 0 or self.value > 120):
            raise ValueError(f"나이는 0–120 범위여야 합니다: {self.value}")

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "Age":
        if not raw or not str(raw).strip():
            return cls(value=None)
        try:
            return cls(value=float(raw))
        except (ValueError, TypeError):
            raise ValueError(f"나이 파싱 실패: {raw!r}")

    @property
    def is_unknown(self) -> bool:
        return self.value is None

    @property
    def is_minor(self) -> bool:
        return self.value is not None and self.value < 18

    @property
    def age_group(self) -> AgeGroup:
        if self.value is None:
            return AgeGroup.UNKNOWN
        if self.value <= 2:
            return AgeGroup.BABY
        if self.value <= 12:
            return AgeGroup.CHILD
        if self.value <= 17:
            return AgeGroup.TEENAGER
        if self.value <= 64:
            return AgeGroup.ADULT
        return AgeGroup.SENIOR

    def __str__(self) -> str:
        return str(self.value) if self.value is not None else "미상"
