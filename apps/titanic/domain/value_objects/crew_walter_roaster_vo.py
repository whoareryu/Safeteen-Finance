from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """모든 VO의 기반."""


@dataclass(frozen=True)
class WalterId(ValueObject):
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Id는 양의 정수여야 합니다.")

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class WalterName(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("이름은 비어 있을 수 없습니다.")
        if len(self.value) > 255:
            raise ValueError("이름은 최대 255자입니다.")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class WalterMemo(ValueObject):
    raw: str

    def is_empty(self) -> bool:
        return not self.raw.strip()

    def __str__(self) -> str:
        return self.raw
