from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.james_director_dto import BookingCommand, PersonCommand
from titanic.app.ports.output.james_director_repository import JamesRepository

logger = logging.getLogger(__name__)


class JamesDirectorPgRepository(JamesRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def receive_uploaded_records(self,person_commands: list[PersonCommand],booking_commands: list[BookingCommand]) -> int:
        logger.info(
            "[James Repository] PersonCommand sample (top 5 of %d): %s",
            len(person_commands),
            person_commands[:5],
        )
        logger.info(
            "[James Repository] BookingCommand sample (top 5 of %d): %s",
            len(booking_commands),
            booking_commands[:5],
        )

        pass

    