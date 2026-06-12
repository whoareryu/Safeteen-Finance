from __future__ import annotations

from dataclasses import dataclass

from titanic.domain.value_objects.passenger_jack_trainer_vo import (
    Age,
    FamilyRelation,
    Gender,
    PassengerId,
    PassengerName,
    SurvivalStatus,
)


@dataclass
class PassengerEntity:
    id: int
    passenger_id: PassengerId | None
    name: PassengerName | None
    gender: Gender
    age: Age
    family_relation: FamilyRelation
    survival_status: SurvivalStatus

    def is_high_risk(self) -> bool:
        """성별 미상 포함 비여성 + 성인(18세 이상) + 혼자 탑승."""
        not_female = not self.gender.is_female()
        adult = not self.age.is_minor
        alone = self.family_relation.is_alone
        return not_female and adult and alone

    def has_family(self) -> bool:
        return not self.family_relation.is_alone

    def record_survival(self, survived: bool) -> None:
        self.survival_status = SurvivalStatus(survived=survived)

    @classmethod
    def from_orm(cls, orm: object) -> PassengerEntity:
        return cls(
            id=orm.id,
            passenger_id=PassengerId(orm.passenger_id) if orm.passenger_id else None,
            name=PassengerName(orm.name) if orm.name else None,
            gender=Gender.from_raw(orm.gender),
            age=Age.from_raw(orm.age),
            family_relation=FamilyRelation.from_raw(orm.sib_sp, orm.parch),
            survival_status=SurvivalStatus.from_raw(orm.survived),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PassengerEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
