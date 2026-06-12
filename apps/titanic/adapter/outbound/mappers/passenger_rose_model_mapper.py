from __future__ import annotations

from titanic.adapter.outbound.orm.passenger_rose_model_orm import RoseModelORM
from titanic.domain.entites.passenger_rose_model_entity import BookingEntity
from titanic.domain.value_objects.passenger_rose_model_vo import (
    Cabin,
    Embarkation,
    Fare,
    PassengerClass,
    PersonReference,
    TicketNumber,
)


class RoseModelMapper:
    """RoseModelORM(bookings) <-> BookingEntity 변환 담당."""

    @staticmethod
    def to_entity(orm: RoseModelORM) -> BookingEntity:
        return BookingEntity(
            id=orm.id,
            person_id=PersonReference(orm.person_id),
            passenger_class=PassengerClass(orm.pclass or "3"),
            ticket_number=TicketNumber(orm.ticket or ""),
            fare=Fare(orm.fare or ""),
            cabin=Cabin(orm.cabin or ""),
            embarkation=Embarkation(orm.embarked or ""),
        )

    @staticmethod
    def to_orm(entity: BookingEntity) -> RoseModelORM:
        return RoseModelORM(
            person_id=entity.person_id.value,
            pclass=entity.passenger_class.value,
            ticket=str(entity.ticket_number),
            fare=entity.fare.raw,
            cabin=entity.cabin.raw,
            embarked=entity.embarkation.raw,
        )
