from __future__ import annotations

import os

from google import genai

from ontology.app.dtos.gemini_dto import GeminiAnswerDto, GeminiQueryDto
from ontology.app.ports.input.gemini_use_case import GeminiUseCase

_MODEL = "gemini-flash-latest"


class GeminiInteractor(GeminiUseCase):
    def __init__(self, api_key: str | None = None, model: str = _MODEL) -> None:
        resolved_key = api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_key:
            raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다 (.env 확인).")
        self._client = genai.Client(api_key=resolved_key)
        self._model = model

    async def ask(self, dto: GeminiQueryDto) -> GeminiAnswerDto:
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=dto.question,
        )
        return GeminiAnswerDto(answer=response.text)
