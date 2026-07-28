from abc import ABC, abstractmethod


class LangchainChatbotGateway(ABC):
    @abstractmethod
    async def chat(self, message: str) -> str: ...
