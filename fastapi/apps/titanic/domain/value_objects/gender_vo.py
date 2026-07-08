from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class GenderType(str, Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Gender:
    value: GenderType

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "Gender":
        if raw is None or str(raw).strip() == "":
            return cls(value=GenderType.UNKNOWN)
        normalized = str(raw).strip().lower()
        if normalized == "male":
            return cls(value=GenderType.MALE)
        if normalized == "female":
            return cls(value=GenderType.FEMALE)
        return cls(value=GenderType.UNKNOWN)

    @property
    def is_female(self) -> bool:
        return self.value == GenderType.FEMALE

    @property
    def is_male(self) -> bool:
        return self.value == GenderType.MALE

    def __str__(self) -> str:
        return self.value.value
