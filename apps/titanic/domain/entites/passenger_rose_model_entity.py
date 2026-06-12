from __future__ import annotations

from dataclasses import dataclass

from titanic.domain.value_objects.passenger_rose_model_vo import (
    Cabin,
    Embarkation,
    Fare,
    PassengerClass,
    PersonReference,
    TicketNumber,
)

    
@dataclass
class BookingEntity:
    """예약(탑승) 도메인 엔티티.
    동등성은 person_id(승객 FK) 기준 — 한 승객은 예약을 하나 가진다.
    """

    id: int                        # DB 대리 PK — 영속성 전용
    person_id: PersonReference     # passengers.id 참조
    passenger_class: PassengerClass
    ticket_number: TicketNumber
    fare: Fare
    cabin: Cabin
    embarkation: Embarkation

    # ── 동등성·해시 (도메인 키 기준) ─────────────────────────
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BookingEntity):
            return False
        return self.person_id == other.person_id

    def __hash__(self) -> int:
        return hash(self.person_id)

    # ── 팩토리 ────────────────────────────────────────────────
    @classmethod
    def from_orm(cls, orm: object) -> BookingEntity:
        return cls(
            id=orm.id,
            person_id=PersonReference(orm.person_id),
            passenger_class=PassengerClass(orm.pclass or "3"),
            ticket_number=TicketNumber(orm.ticket or ""),
            fare=Fare(orm.fare or ""),
            cabin=Cabin(orm.cabin or ""),
            embarkation=Embarkation(orm.embarked or ""),
        )

    # ── 도메인 행위 ───────────────────────────────────────────
    def is_first_class(self) -> bool:
        return self.passenger_class.is_first_class()

    def boarded_at(self) -> str | None:
        return self.embarkation.port_name()

    def has_cabin(self) -> bool:
        return self.cabin.is_assigned()

    def deck(self) -> str | None:
        return self.cabin.deck()

    def fare_amount(self) -> float | None:
        return self.fare.as_float()
