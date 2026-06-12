from __future__ import annotations

from dataclasses import dataclass

from titanic.domain.value_objects.passenger_jack_trainer_vo import (
    Age,
    Gender,
    Parch,
    PassengerId,
    PassengerName,
    SibSp,
    SurvivedStatus,
)


@dataclass
class PassengerEntity:
    """승객 도메인 엔티티. 동등성은 passenger_id(도메인 식별자) 기준."""

    id: int  # DB 대리 PK — 영속성 레이어 전용, 도메인 동등성에 미사용
    passenger_id: PassengerId
    name: PassengerName
    gender: Gender
    age: Age
    sib_sp: SibSp
    parch: Parch
    survived: SurvivedStatus

    # ── 동등성·해시 (도메인 키 기준) ─────────────────────────
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PassengerEntity):
            return False
        return self.passenger_id == other.passenger_id

    def __hash__(self) -> int:
        return hash(self.passenger_id)

    # ── 팩토리 ────────────────────────────────────────────────
    @classmethod
    def from_orm(cls, orm: object) -> PassengerEntity:
        return cls(
            id=orm.id,
            passenger_id=PassengerId(orm.passenger_id),
            name=PassengerName(orm.name),
            gender=Gender(orm.gender or "unknown"),
            age=Age(orm.age or ""),
            sib_sp=SibSp(orm.sib_sp or "0"),
            parch=Parch(orm.parch or "0"),
            survived=SurvivedStatus(orm.survived or ""),
        )

    # ── 도메인 행위 ───────────────────────────────────────────
    def did_survive(self) -> bool | None:
        return self.survived.survived()

    def is_traveling_alone(self) -> bool:
        return self.sib_sp.as_int() + self.parch.as_int() == 0

    def total_relatives(self) -> int:
        return self.sib_sp.as_int() + self.parch.as_int()
