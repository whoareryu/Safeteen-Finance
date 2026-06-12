from __future__ import annotations

import logging
from typing import Any

from apps.titanic.adapter.inbound.api.schemas.crew_james_director_schema import JamesDirectorSchema
from titanic.app.dtos.james_director_dto import BookingCommand, JamesDirectorResponse, PassengerCommand
from titanic.app.ports.input.james_director_use_case import JamesDirectorUseCase
from titanic.app.ports.output.james_director_repository import JamesDirectorRepository

logger = logging.getLogger(__name__)


class JamesDirectorInteractor(JamesDirectorUseCase):
    def __init__(self, repository: JamesDirectorRepository) -> None:
        self._repository = repository
        
    async def upload_titanic_file(self, schema: list[JamesDirectorSchema]) -> JamesDirectorResponse:
        logger.info(
            "[James UseCase] schema from router (top 5 of %d rows): %s",
            len(schema),
            schema[:5],
        )

        passenger_commands: list[PassengerCommand] = []
        booking_commands: list[BookingCommand] = []

        for record in schema:
            passenger_commands.append(
                PassengerCommand(
                    passenger_id=record.passenger_id or "",
                    name=record.name or "",
                    gender=record.gender or "",
                    age=record.age or "",
                    sib_sp=record.sib_sp or "",
                    parch=record.parch or "",
                    survived=record.survived or "",
                )
            )
            booking_commands.append(
                BookingCommand(
                    pclass=record.pclass or "",
                    ticket=record.ticket or "",
                    fare=record.fare or "",
                    cabin=record.cabin or "",
                    embarked=record.embarked or "",
                )
            )

        saved = await self._repository.upload_titanic_file(
            passenger_commands,
            booking_commands,
        )
        return JamesDirectorResponse(answer=f"INSERT 완료: {saved}건")
