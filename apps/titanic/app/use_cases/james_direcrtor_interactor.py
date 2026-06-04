from __future__ import annotations

import logging
from typing import Any

from titanic.adapter.inbound.api.schemas.james_director_schema import TitanicRecordSchema
from titanic.app.ports.input.james_director_use_case import JamesDirectorUseCase
from titanic.app.ports.output.james_director_repository import JamesRepository
from titanic.app.dtos.james_director_dto import BookingCommand, PersonCommand
from titanic.adapter.outbound.pg.james_director_pg_repository import JamesDirectorPgRepository

logger = logging.getLogger(__name__)


class JamesDirectorInteractor(JamesDirectorUseCase):
    def __init__(self) -> None:
        pass

    async def receive_uploaded_records(self, schema: list[TitanicRecordSchema]) -> dict[str, Any]:
        logger.info(
            "[James UseCase] schema from router (top 5 of %d rows): %s",
            len(schema),
            schema[:5],
        )

        # schema 를 PersonCommand 및 BookingCommand 로 나눠서 옮겨담기
        person_commands: list[PersonCommand] = []
        booking_commands: list[BookingCommand] = []

        for record in schema:
            person_commands.append(PersonCommand(
                passenger_id=record.passenger_id or "",
                name=record.name or "",
                gender=record.gender or "",
                age=record.age or "",
                sib_sp=record.sib_sp or "",
                parch=record.parch or "",
                survived=record.survived or "",
            ))
            booking_commands.append(BookingCommand(
                pclass=record.pclass or "",
                ticket=record.ticket or "",
                fare=record.fare or "",
                cabin=record.cabin or "",
                embarked=record.embarked or "",
            ))

        repository : JamesRepository = JamesDirectorPgRepository(None)

        await repository.receive_uploaded_records(person_commands, booking_commands)

        pass

