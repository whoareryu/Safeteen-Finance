from abc import ABC, abstractmethod

from ontology.app.dtos.gemini_dto import GeminiAnswerDto, GeminiQueryDto


class GeminiUseCase(ABC):
    @abstractmethod
    async def ask(self, dto: GeminiQueryDto) -> GeminiAnswerDto: ...
