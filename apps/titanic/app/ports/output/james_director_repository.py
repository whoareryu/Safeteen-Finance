from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class JamesRepository(ABC):
    @abstractmethod
    async def receive_uploaded_records(self,
        person_commands: list[PersonCommand],
        booking_commands: list[BookingCommand]) -> int:
        pass

