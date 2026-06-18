from __future__ import annotations

from dataclasses import dataclass

from titanic.domain.value_objects.gender_vo import Gender
from titanic.domain.value_objects.age_vo import Age
from titanic.domain.value_objects.sibsp_vo import SibSp
from titanic.domain.value_objects.parch_vo import Parch
from titanic.domain.value_objects.survived_vo import Survived


@dataclass
class PassengerEntity:
    id: int
    passenger_id: str | None
    name: str | None
    gender: Gender
    age: Age
    sib_sp: SibSp
    parch: Parch
    survived: Survived

    @property
    def is_alone(self) -> bool:
        return self.sib_sp.value == 0 and self.parch.value == 0

    def is_high_risk(self) -> bool:
        """성별 미상 포함 비여성 + 성인(18세 이상) + 혼자 탑승."""
        not_female = not self.gender.is_female
        adult = not self.age.is_minor
        return not_female and adult and self.is_alone

    def has_family(self) -> bool:
        return not self.is_alone

    def record_survival(self, survived: bool) -> None:
        self.survived = Survived(value=survived)

    @classmethod
    def from_orm(cls, orm: object) -> PassengerEntity:
        return cls(
            id=orm.id,
            passenger_id=orm.passenger_id or None,
            name=orm.name or None,
            gender=Gender.from_raw(orm.gender),
            age=Age.from_raw(orm.age),
            sib_sp=SibSp.from_raw(orm.sib_sp),
            parch=Parch.from_raw(orm.parch),
            survived=Survived.from_raw(orm.survived),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PassengerEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
