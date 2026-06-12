from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """모든 VO의 기반. 동등성 비교는 dataclass가 자동 처리."""


# ── PersonReference ────────────────────────────────────────────
@dataclass(frozen=True)
class PersonReference(ValueObject):
    """passengers.id 를 참조하는 FK VO. 도메인이 ORM 관계를 직접 보유하지 않도록 격리."""
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(f"PersonReference는 양의 정수여야 합니다. 입력값: {self.value}")

    def __str__(self) -> str:
        return str(self.value)


# ── PassengerClass ─────────────────────────────────────────────
_ALLOWED_CLASSES = frozenset({"1", "2", "3"})

@dataclass(frozen=True)
class PassengerClass(ValueObject):
    """티켓 등급 (1=1등석, 2=2등석, 3=3등석)."""
    value: str

    def __post_init__(self) -> None:
        if self.value not in _ALLOWED_CLASSES:
            raise ValueError(f"PassengerClass는 {_ALLOWED_CLASSES} 중 하나여야 합니다.")

    def is_first_class(self) -> bool:
        return self.value == "1"

    def is_second_class(self) -> bool:
        return self.value == "2"

    def is_third_class(self) -> bool:
        return self.value == "3"

    def label(self) -> str:
        return {"1": "1등석", "2": "2등석", "3": "3등석"}[self.value]


# ── TicketNumber ───────────────────────────────────────────────
@dataclass(frozen=True)
class TicketNumber(ValueObject):
    """티켓 번호. 최대 128자."""
    value: str

    def __post_init__(self) -> None:
        if len(self.value) > 128:
            raise ValueError("TicketNumber는 최대 128자입니다.")

    def is_known(self) -> bool:
        return bool(self.value and self.value.strip())

    def __str__(self) -> str:
        return self.value


# ── Fare ───────────────────────────────────────────────────────
@dataclass(frozen=True)
class Fare(ValueObject):
    """탑승 요금. ORM에서 str로 저장, 미상이면 raw='' 허용."""
    raw: str

    def as_float(self) -> float | None:
        try:
            return float(self.raw)
        except (ValueError, TypeError):
            return None

    def is_known(self) -> bool:
        return self.as_float() is not None

    def is_free(self) -> bool:
        v = self.as_float()
        return v is not None and v == 0.0

    def is_expensive(self, threshold: float = 100.0) -> bool:
        v = self.as_float()
        return v is not None and v >= threshold


# ── Cabin ──────────────────────────────────────────────────────
@dataclass(frozen=True)
class Cabin(ValueObject):
    """객실 번호. 미배정이면 raw='' 허용."""
    raw: str

    def is_assigned(self) -> bool:
        return bool(self.raw and self.raw.strip())

    def deck(self) -> str | None:
        """객실 첫 글자(갑판 식별자)를 반환. 미배정이면 None."""
        if self.is_assigned():
            return self.raw.strip()[0].upper()
        return None

    def __str__(self) -> str:
        return self.raw or "미배정"


# ── Embarkation ────────────────────────────────────────────────
_PORT_NAMES: dict[str, str] = {
    "C": "Cherbourg",
    "Q": "Queenstown",
    "S": "Southampton",
}

@dataclass(frozen=True)
class Embarkation(ValueObject):
    """탑승 항구 코드 (C/Q/S). 미상이면 raw='' 허용."""
    raw: str

    def __post_init__(self) -> None:
        normalized = self.raw.upper().strip() if self.raw else ""
        if normalized and normalized not in _PORT_NAMES:
            raise ValueError(f"Embarkation은 {list(_PORT_NAMES.keys())} 중 하나여야 합니다.")
        object.__setattr__(self, "raw", normalized)

    def port_name(self) -> str | None:
        return _PORT_NAMES.get(self.raw)

    def is_known(self) -> bool:
        return bool(self.raw)

    def __str__(self) -> str:
        return self.port_name() or "미상"
