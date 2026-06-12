from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class PassengerId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("PassengerId는 빈 값일 수 없습니다.")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PassengerName:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("승객 이름은 빈 값일 수 없습니다.")
        if len(self.value) > 200:
            raise ValueError("승객 이름은 200자를 초과할 수 없습니다.")

    @property
    def full_name(self) -> str:
        return self.value

    @property
    def normalized(self) -> str:
        return self.value.strip()

    def __str__(self) -> str:
        return self.value


class GenderType(Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Gender:
    value: GenderType

    @classmethod
    def from_raw(cls, raw: str | None) -> Gender:
        if not raw:
            return cls(GenderType.UNKNOWN)
        normalized = raw.strip().lower()
        if normalized == "male":
            return cls(GenderType.MALE)
        if normalized == "female":
            return cls(GenderType.FEMALE)
        return cls(GenderType.UNKNOWN)

    def is_female(self) -> bool:
        return self.value == GenderType.FEMALE


@dataclass(frozen=True)
class Age:
    value: float | None

    def __post_init__(self) -> None:
        if self.value is not None and (self.value < 0 or self.value > 120):
            raise ValueError(f"나이는 0–120 범위여야 합니다: {self.value}")

    @classmethod
    def from_raw(cls, raw: str | None) -> Age:
        if not raw or not str(raw).strip():
            return cls(None)
        try:
            return cls(float(raw))
        except (ValueError, TypeError):
            raise ValueError(f"나이 파싱 실패: {raw!r}")

    @property
    def is_unknown(self) -> bool:
        return self.value is None

    @property
    def is_minor(self) -> bool:
        return self.value is not None and self.value < 18


@dataclass(frozen=True)
class FamilyRelation:
    sib_sp: int
    parch: int

    def __post_init__(self) -> None:
        if self.sib_sp < 0:
            raise ValueError("sib_sp는 0 이상이어야 합니다.")
        if self.parch < 0:
            raise ValueError("parch는 0 이상이어야 합니다.")

    @classmethod
    def from_raw(cls, sib_sp_raw: str | None, parch_raw: str | None) -> FamilyRelation:
        def _to_int(v: str | None) -> int:
            if v is None:
                return 0
            try:
                return int(v)
            except (ValueError, TypeError):
                return 0

        return cls(sib_sp=_to_int(sib_sp_raw), parch=_to_int(parch_raw))

    @property
    def total_family_size(self) -> int:
        return self.sib_sp + self.parch

    @property
    def is_alone(self) -> bool:
        return self.total_family_size == 0


@dataclass(frozen=True)
class SurvivalStatus:
    survived: bool | None

    @classmethod
    def from_raw(cls, raw: str | None) -> SurvivalStatus:
        if not raw or not str(raw).strip():
            return cls(None)
        if raw == "1":
            return cls(True)
        if raw == "0":
            return cls(False)
        raise ValueError(f"SurvivalStatus 파싱 실패: {raw!r}")

    @property
    def is_unknown(self) -> bool:
        return self.survived is None
