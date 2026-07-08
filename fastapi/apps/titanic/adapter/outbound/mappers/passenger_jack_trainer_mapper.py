from __future__ import annotations

from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerORM
from titanic.domain.entities.passenger_jack_trainer_entity import PassengerEntity
from titanic.domain.value_objects.gender_vo import Gender
from titanic.domain.value_objects.age_vo import Age
from titanic.domain.value_objects.sibsp_vo import SibSp
from titanic.domain.value_objects.parch_vo import Parch
from titanic.domain.value_objects.survived_vo import Survived


class JackTrainerMapper:
    """JackTrainerORM(passengers) <-> PassengerEntity 변환 담당."""

    @staticmethod
    def to_entity(orm: JackTrainerORM) -> PassengerEntity:
        return PassengerEntity(
            id=orm.id,
            passenger_id=orm.passenger_id or None,
            name=orm.name or None,
            gender=Gender.from_raw(orm.gender),
            age=Age.from_raw(orm.age),
            sib_sp=SibSp.from_raw(orm.sib_sp),
            parch=Parch.from_raw(orm.parch),
            survived=Survived.from_raw(orm.survived),
        )

    @staticmethod
    def to_orm(entity: PassengerEntity) -> JackTrainerORM:
        # NOTE: JackTrainerORM has no 'id' kwarg — TypeError is the documented bug (Red test).
        return JackTrainerORM(
            id=entity.id,
            passenger_id=entity.passenger_id or "",
            name=entity.name or "",
            gender=entity.gender.value.value,
            age=str(entity.age.value) if not entity.age.is_unknown else "",
            sib_sp=str(entity.sib_sp.value),
            parch=str(entity.parch.value),
            survived=(
                "1" if entity.survived.value is True
                else "0" if entity.survived.value is False
                else ""
            ),
        )
