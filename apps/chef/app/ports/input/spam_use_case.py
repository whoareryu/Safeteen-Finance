from abc import ABC, abstractmethod

from chef.app.dtos.spam_dto import SpamClassificationCommand, SpamClassificationResult


class SpamUseCase(ABC):
    @abstractmethod
    async def classify(self, cmd: SpamClassificationCommand) -> SpamClassificationResult: ...
