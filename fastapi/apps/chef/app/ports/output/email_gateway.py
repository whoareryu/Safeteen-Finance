from abc import ABC, abstractmethod

from chef.app.dtos.email_dto import EmailTaskDto


class EmailGateway(ABC):
    @abstractmethod
    async def send(self, dto: EmailTaskDto) -> None: ...
