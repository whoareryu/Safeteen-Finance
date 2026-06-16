from dataclasses import dataclass


@dataclass(frozen=True)
class CalTesterQuery:
    id: int
    name: str


@dataclass(frozen=True)
class CalTesterResponse:
    id: int
    name: str


@dataclass(frozen=True)
class CalTesterPassengerData:
    survived: int
    age: float
    sib_sp: int
    parch: int
    gender: int  # 0=male, 1=female