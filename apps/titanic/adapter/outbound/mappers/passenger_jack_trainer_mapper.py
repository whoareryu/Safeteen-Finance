from __future__ import annotations

from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerORM
from titanic.domain.entities.passenger_jack_trainer_entity import PassengerEntity
from titanic.domain.value_objects.passenger_jack_trainer_vo import (
    Age,
    FamilyRelation,
    Gender,
    PassengerId,
    PassengerName,
    SurvivalStatus,
)


class JackTrainerMapper:
    """JackTrainerORM(passengers) <-> PassengerEntity 변환 담당."""

    @staticmethod
    def to_entity(orm: JackTrainerORM) -> PassengerEntity:
        return PassengerEntity(
            id=orm.id,
            passenger_id=PassengerId(orm.passenger_id) if orm.passenger_id else None,
            name=PassengerName(orm.name) if orm.name else None,
            gender=Gender.from_raw(orm.gender),
            age=Age.from_raw(orm.age),
            family_relation=FamilyRelation.from_raw(orm.sib_sp, orm.parch),
            survival_status=SurvivalStatus.from_raw(orm.survived),
        )

    @staticmethod
    def to_orm(entity: PassengerEntity) -> JackTrainerORM:
        # NOTE: JackTrainerORM has no 'id' kwarg — TypeError is the documented bug (Red test).
        return JackTrainerORM(
            id=entity.id,
            passenger_id=str(entity.passenger_id) if entity.passenger_id else "",
            name=str(entity.name) if entity.name else "",
            gender=entity.gender.value.value,
            age=str(entity.age.value) if not entity.age.is_unknown else "",
            sib_sp=str(entity.family_relation.sib_sp),
            parch=str(entity.family_relation.parch),
            survived=(
                "1" if entity.survival_status.survived is True
                else "0" if entity.survival_status.survived is False
                else ""
            ),
        )
