from __future__ import annotations

from abc import ABC, abstractmethod

from community.app.dtos.receiver_dto import ReceiverCommand, ReceiverResult


class ReceiverUseCase(ABC):
    @abstractmethod
    async def save(self, cmd: ReceiverCommand) -> ReceiverResult: ...
