from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.crew_james_director_schema import JamesDirectorSchema
from titanic.app.dtos.crew_james_director_dto import (
    BookingCommand,
    JamesDirectorQuery,
    JamesDirectorResponse,
    JamesIntroduceResponse,
    PassengerCommand,
)
from titanic.app.ports.input.crew_james_director_use_case import JamesDirectorUseCase
from titanic.app.ports.output.crew_james_director_port import JamesDirectorPort

logger = logging.getLogger(__name__)


class JamesDirectorInteractor(JamesDirectorUseCase):
    def __init__(self, repository: JamesDirectorPort) -> None:
        self._repository = repository

    async def upload_titanic_file(self, rows: list[dict]) -> dict:
        logger.info("[James UseCase] rows from router (top 5 of %d): %s", len(rows), rows[:5])

        passenger_commands: list[PassengerCommand] = []
        booking_commands: list[BookingCommand] = []

        for r in rows:
            passenger_commands.append(PassengerCommand(
                passenger_id=r.get("passenger_id") or "",
                name=r.get("name") or "",
                gender=r.get("gender") or "",
                age=r.get("age") or "",
                sib_sp=r.get("sib_sp") or "",
                parch=r.get("parch") or "",
                survived=r.get("survived") or "",
            ))
            booking_commands.append(BookingCommand(
                pclass=r.get("pclass") or "",
                ticket=r.get("ticket") or "",
                fare=r.get("fare") or "",
                cabin=r.get("cabin") or "",
                embarked=r.get("embarked") or "",
            ))

        saved = await self._repository.receive_uploaded_records(passenger_commands, booking_commands)
        return {"saved": saved}

    async def introduce_myself(self, schema) -> JamesIntroduceResponse:
        schema = JamesDirectorSchema(id=6, name="제임스 카메론 (James Cameron)")
        return JamesIntroduceResponse(id=schema.id, name=schema.name)
