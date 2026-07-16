from abc import ABC, abstractmethod


class TelegramGateway(ABC):
    @abstractmethod
    async def send(self, text: str) -> None: ...
