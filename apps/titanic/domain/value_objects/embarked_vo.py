from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PortType(str, Enum):
    CHERBOURG = "C"
    QUEENSTOWN = "Q"
    SOUTHAMPTON = "S"


_PORT_LABELS: dict[str, str] = {
    "C": "셰르부르",
    "Q": "퀸즈타운",
    "S": "사우샘프턴",
}


@dataclass(frozen=True)
class Embarked:
    raw: str

    def __post_init__(self) -> None:
        normalized = self.raw.upper().strip() if self.raw else ""
        if normalized and normalized not in _PORT_LABELS:
            raise ValueError(f"Embarked는 {list(_PORT_LABELS.keys())} 중 하나여야 합니다.")
        object.__setattr__(self, "raw", normalized)

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> "Embarked":
        return cls(raw=raw or "")

    def port_name(self) -> Optional[str]:
        return _PORT_LABELS.get(self.raw)

    @property
    def is_known(self) -> bool:
        return bool(self.raw)

    @property
    def label(self) -> str:
        return _PORT_LABELS.get(self.raw, "미상")

    def __str__(self) -> str:
        return self.label
