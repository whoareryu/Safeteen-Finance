from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.adapter.outbound.orm.booking_orm import TitanicBookingORM
from titanic.adapter.outbound.orm.person_orm import TitanicPersonORM
from titanic.app.dtos.james_director_dto import BookingCommand, PersonCommand
from titanic.app.ports.output.james_director_repository import JamesRepository

logger = logging.getLogger(__name__)

_INSERT_BATCH_SIZE = 500


class JamesDirectorPgRepository(JamesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upload_titanic_file(
        self,
        person_commands: list[PersonCommand],
        booking_commands: list[BookingCommand],
    ) -> int:
        if len(person_commands) != len(booking_commands):
            raise ValueError(
                f"PersonCommand({len(person_commands)})와 BookingCommand({len(booking_commands)}) 개수가 다릅니다."
            )
        if not person_commands:
            return 0

        inserted = 0
        for batch_start in range(0, len(person_commands), _INSERT_BATCH_SIZE):
            batch_person = person_commands[batch_start : batch_start + _INSERT_BATCH_SIZE]
            batch_booking = booking_commands[batch_start : batch_start + _INSERT_BATCH_SIZE]

            persons = [
                TitanicPersonORM(
                    passenger_id=person_cmd.passenger_id,
                    name=person_cmd.name,
                    gender=person_cmd.gender,
                    age=person_cmd.age,
                    sib_sp=person_cmd.sib_sp,
                    parch=person_cmd.parch,
                    survived=person_cmd.survived,
                )
                for person_cmd in batch_person
            ]
            self.session.add_all(persons)
            await self.session.flush()

            bookings = [
                TitanicBookingORM(
                    person_id=person.id,
                    pclass=booking_cmd.pclass,
                    ticket=booking_cmd.ticket,
                    fare=booking_cmd.fare,
                    cabin=booking_cmd.cabin,
                    embarked=booking_cmd.embarked,
                )
                for person, booking_cmd in zip(persons, batch_booking, strict=True)
            ]
            self.session.add_all(bookings)
            await self.session.flush()

            inserted += len(batch_person)

        logger.info("[James Repository] INSERT flush 완료: %d건", inserted)
        return inserted
