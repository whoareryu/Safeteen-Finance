from abc import ABC, abstractmethod


class WebFetcherPort(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> str: ...
