from abc import ABC, abstractmethod

from ontology.app.dtos.intent_dto import IntentDto


class IntentClassificationGateway(ABC):
    @abstractmethod
    async def classify(self, question: str) -> IntentDto: ...
