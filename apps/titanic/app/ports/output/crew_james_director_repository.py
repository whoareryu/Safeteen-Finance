from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_james_director_dto import (
    BookingCommand,
    JamesDirectorQuery,
    JamesDirectorResponse,
    PassengerCommand,
)


class JamesDirectorRepository(ABC):
    @abstractmethod
    async def receive_uploaded_records(
        self,
        passenger_commands: list[PassengerCommand],
        booking_commands: list[BookingCommand],
    ) -> int:
        pass

    @abstractmethod
    async def introduce_myself(self, query: JamesDirectorQuery) -> JamesDirectorResponse:
        pass
