from dataclasses import dataclass


@dataclass(frozen=True)
class JackTrainerQuery:
    id: int
    name: str


@dataclass(frozen=True)
class JackTrainerResponse:
    id: int
    name: str


@dataclass(frozen=True)
class JackTrainerPassengerData:
    survived: int
    age: float
    sib_sp: int
    parch: int
    gender: int  # 0=male, 1=female