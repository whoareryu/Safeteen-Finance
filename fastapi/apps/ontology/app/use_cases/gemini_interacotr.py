from __future__ import annotations

from google import genai

from core.llm.gemini_compatible_local_llm_client import gemini_compatible_local_llm_client
from ontology.app.dtos.gemini_dto import GeminiAnswerDto, GeminiQueryDto
from ontology.app.ports.input.gemini_use_case import GeminiUseCase

_MODEL = "gemini-flash-latest"


class GeminiInteractor(GeminiUseCase):
    def __init__(self, api_key: str | None = None, model: str = _MODEL) -> None:
        resolved_key = api_key or gemini_compatible_local_llm_client.get_secret("GEMINI_API_KEY")
        self._client = genai.Client(api_key=resolved_key)
        self._model = model

    async def ask(self, dto: GeminiQueryDto) -> GeminiAnswerDto:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=dto.question,
        )
        return GeminiAnswerDto(answer=response.text)
