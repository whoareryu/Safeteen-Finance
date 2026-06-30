from abc import ABC, abstractmethod

from chef.app.dtos.email_dto import EmailTaskDto


class EmailUseCase(ABC):
    @abstractmethod
    async def execute(self, to: str, prompt: str) -> EmailTaskDto: ...
