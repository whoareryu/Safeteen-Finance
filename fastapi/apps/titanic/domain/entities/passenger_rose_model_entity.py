from __future__ import annotations

from dataclasses import dataclass

from titanic.domain.value_objects.pclass_vo import PClass, PClassType
from titanic.domain.value_objects.ticket_vo import TicketNumber
from titanic.domain.value_objects.fare_vo import Fare
from titanic.domain.value_objects.cabin_vo import Cabin
from titanic.domain.value_objects.embarked_vo import Embarked


@dataclass
class BookingEntity:
    """예약(탑승) 도메인 엔티티.
    동등성은 person_id(승객 FK) 기준 — 한 승객은 예약을 하나 가진다.
    """

    id: int
    person_id: int
    pclass: PClass
    ticket_number: TicketNumber
    fare: Fare
    cabin: Cabin
    embarked: Embarked

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BookingEntity):
            return False
        return self.person_id == other.person_id

    def __hash__(self) -> int:
        return hash(self.person_id)

    @classmethod
    def from_orm(cls, orm: object) -> BookingEntity:
        raw_pclass = str(orm.pclass) if orm.pclass else "3"
        return cls(
            id=orm.id,
            person_id=orm.person_id,
            pclass=PClass(value=PClassType(int(raw_pclass))),
            ticket_number=TicketNumber(orm.ticket or ""),
            fare=Fare(orm.fare or ""),
            cabin=Cabin(orm.cabin or ""),
            embarked=Embarked(orm.embarked or ""),
        )

    def is_first_class(self) -> bool:
        return self.pclass.is_first_class

    def boarded_at(self) -> str | None:
        return self.embarked.port_name()

    def has_cabin(self) -> bool:
        return self.cabin.is_assigned

    def deck(self) -> str | None:
        return self.cabin.deck

    def fare_amount(self) -> float | None:
        return self.fare.as_float()
