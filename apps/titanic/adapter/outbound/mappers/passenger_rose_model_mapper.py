from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from titanic.adapter.outbound.orm.passenger_rose_model_strategies import RoseModelORM

from titanic.domain.entities.passenger_rose_model_entity import BookingEntity
from titanic.domain.value_objects.pclass_vo import PClass, PClassType
from titanic.domain.value_objects.ticket_vo import TicketNumber
from titanic.domain.value_objects.fare_vo import Fare
from titanic.domain.value_objects.cabin_vo import Cabin
from titanic.domain.value_objects.embarked_vo import Embarked


class RoseModelMapper:
    """RoseModelORM(bookings) <-> BookingEntity 변환 담당."""

    @staticmethod
    def to_entity(orm: "RoseModelORM") -> BookingEntity:
        raw_pclass = str(orm.pclass) if orm.pclass else "3"
        return BookingEntity(
            id=orm.id,
            person_id=orm.person_id,
            pclass=PClass(value=PClassType(int(raw_pclass))),
            ticket_number=TicketNumber(orm.ticket or ""),
            fare=Fare(orm.fare or ""),
            cabin=Cabin(orm.cabin or ""),
            embarked=Embarked(orm.embarked or ""),
        )

    @staticmethod
    def to_orm(entity: BookingEntity) -> "RoseModelORM":
        return None  # NOTE: RoseModelORM 파일 미존재 — 구현 대기 중
